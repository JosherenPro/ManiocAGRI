import logging
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from core.config import settings

# Try to import Cerebras client if available
client = None
try:
    from cerebras.cloud.sdk import Cerebras

    if settings.CEREBRAS_API_KEY:
        client = Cerebras(api_key=settings.CEREBRAS_API_KEY)
except Exception:
    client = None

logger = logging.getLogger(__name__)


async def chat_with_ai(prompt: str, history: list = None):
    """
    Wrapper to call external AI provider (Cerebras) with resilient fallback.
    Tries a prioritized list of models and falls back to a local mock if none are
    available or if an unrecoverable error (quota/auth) occurs.
    """
    # Preferred models to try in order. You can override with
    # env `CEREBRAS_PREFERRED_MODELS` (comma-separated). Default prefers llama-3.3-70b.
    env_models = os.getenv("CEREBRAS_PREFERRED_MODELS", "").strip()
    default_models = [
        "gpt-oss-120b",
        "llama-3.3-70b",
        "llama3.1-70b",
        "llama3.1-13b",
        "llama-3.1-7b",
    ]

    if env_models:
        # user provided list (highest priority)
        provided = [m.strip() for m in env_models.split(",") if m.strip()]
        # keep order, then append defaults that are not present
        preferred_models = provided + [m for m in default_models if m not in provided]
    else:
        preferred_models = default_models

    # If we have a client, attempt to discover available models and promote
    # `llama-3.3-70b` (or any model the user explicitly requested) to the front
    if client:
        try:
            # Best-effort: try to list models if SDK exposes that API
            available = None
            if hasattr(client, "models") and hasattr(client.models, "list"):
                available = [m.id for m in client.models.list()]
            elif hasattr(client, "list_models"):
                available = [m.id for m in client.list_models()]

            if available:
                # If `llama-3.3-70b` is available, ensure it's first
                if "llama-3.3-70b" in available:
                    preferred_models = ["llama-3.3-70b"] + [
                        m for m in preferred_models if m != "llama-3.3-70b"
                    ]
                else:
                    # promote the first available preferred model we support
                    for m in preferred_models:
                        if m in available:
                            preferred_models = [m] + [
                                x for x in preferred_models if x != m
                            ]
                            break
        except Exception:
            # non-fatal: keep preferred_models as-is
            logger.debug(
                "Unable to discover remote models; using configured preferred_models"
            )

    system_prompt = (
        "Tu es l'assistant intelligent de ManiocAgri, une plateforme agricole au "
        "Togo. Tu aides les utilisateurs (producteurs, clients, admins) sur des "
        "sujets comme le prix du manioc, les livraisons, et l'utilisation de la "
        "plateforme. Réponds de manière concise et professionnelle en français."
    )

    if client:
        for model_name in preferred_models:
            try:
                logger.info("Attempting model %s", model_name)
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    model=model_name,
                )

                if getattr(response, "choices", None) and len(response.choices) > 0:
                    try:
                        return response.choices[0].message.content
                    except Exception:
                        return getattr(
                            response.choices[0],
                            "text",
                            "Désolé, réponse non disponible.",
                        )

                logger.warning(
                    "Empty response from model %s, trying next model", model_name
                )

            except Exception as e:
                err_low = str(e).lower()
                logger.warning("Model %s failed: %s", model_name, err_low)
                # Immediate user-friendly responses for common errors
                if ("429" in err_low) or ("quota" in err_low) or ("rate" in err_low):
                    logger.exception("Quota/rate error from external provider")
                    return "🔄 L'assistant externe est temporairement indisponible (quota/rate limit)."
                if (
                    ("401" in err_low)
                    or ("403" in err_low)
                    or ("api key" in err_low)
                    or ("invalid" in err_low)
                ):
                    logger.exception("Authentication error with external provider")
                    return (
                        "🔑 Clé API invalide ou non fournie pour l'assistant externe."
                    )
                # otherwise try next model

    # Local fallback (mock) when no external client or after all model attempts fail
    logger.info("Using local mock AI fallback for prompt: %s", prompt[:120])
    low = prompt.lower()
    if "résumé" in low or "resume" in low or "présentation" in low:
        return (
            "ManiocAgri est une plateforme qui connecte producteurs, clients et livreurs, "
            "permettant la gestion des produits, commandes et données de terrain."
        )
    if "prix" in low and "manioc" in low:
        return "Le prix du manioc varie selon le producteur et la saison. Consulte le catalogue pour les prix actuels."
    preview = prompt if len(prompt) <= 300 else prompt[:300] + "..."
    return f"[MODE DÉGRADÉ] Réponse factice pour tests — Vous avez demandé: {preview}"


class DemandPredictor:
    @staticmethod
    def predict(order_data: list):
        """
        Prédiction de la demande basée sur l'historique des commandes.
        order_data: liste d'objets avec {created_at, total_price}
        """
        if len(order_data) < 5:
            return {
                "forecast": [],
                "msg": "Pas assez de données pour une prédiction fiable.",
            }

        df = pd.DataFrame(order_data)
        df["created_at"] = pd.to_datetime(df["created_at"])
        # Normaliser à minuit pour aggréger par jour
        df["date"] = df["created_at"].dt.normalize()

        # Aggrégation par jour
        daily_sales = df.groupby("date").size().reset_index(name="count")

        if len(daily_sales) < 2:
            return {
                "forecast": [],
                "msg": "Données historiques sur une seule journée. Prédiction impossible.",
            }

        # Conversion des dates en nombres de jours depuis le début
        start_date = daily_sales["date"].min()
        daily_sales["day_num"] = (daily_sales["date"] - start_date).dt.days

        # Modèle de régression linéaire simple pour la tendance
        X = daily_sales[["day_num"]].values
        y = daily_sales["count"].values

        reg_model = LinearRegression()
        reg_model.fit(X, y)

        # Prédiction pour les 7 prochains jours
        last_day = daily_sales["day_num"].max()
        future_days = np.array([[last_day + i] for i in range(1, 8)])
        predictions = reg_model.predict(future_days)

        forecast = []
        for i, pred in enumerate(predictions):
            future_date = start_date + timedelta(days=int(last_day + i + 1))
            forecast.append(
                {
                    "date": future_date.strftime("%Y-%m-%d"),
                    "predicted_orders": max(0, int(round(pred))),
                }
            )

        return forecast
