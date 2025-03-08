import os
import json
import logging

logger = logging.getLogger(__name__)


def load_expressions(guild_id):
    dir = "serverdata"
    filepath = f"{dir}/{guild_id}.json"

    if not os.path.exists(dir):
        os.makedirs(dir)

    if not os.path.exists(filepath):
        with open(filepath, "w") as file:
            json.dump({"info": {}, "expressions": []}, file)

    try:
        with open(filepath, "r") as file:
            logger.info(f"Loading expressions for guild {
                        guild_id} from {filepath}")
            return json.load(file)
    except (json.JSONDecodeError) as e:
        logger.error(f"Failed to load expressions for guild {guild_id}: {e}")
        return {"info": {}, "expressions": []}


def save_expressions(guild_id, data):
    dir = "serverdata"
    filepath = f"{dir}/{guild_id}.json"

    if not os.path.exists(dir):
        os.makedirs(dir)

    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)
        logger.info(f"Expressions for guild {guild_id} saved to {filepath}")
