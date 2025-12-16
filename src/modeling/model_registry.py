import mlflow
import dagshub
import json
from pathlib import Path
from mlflow import MlflowClient
import logging


# create logger
logger = logging.getLogger("model_registry")
logger.setLevel(logging.DEBUG)

# console handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# file handler
file_handler = logging.FileHandler('model_registry.log')
file_handler.setLevel(logging.DEBUG)


# create a fomratter
formatter = logging.Formatter(fmt='[%(asctime)s] (line %(lineno)d) - %(name)s - %(levelname)s in %(module)s: %(message)s')
# add formatter to handler
handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# ADD BOTH HANDLERS
logger.addHandler(handler)
logger.addHandler(file_handler)

# initialize dagshub
import dagshub
dagshub.init(repo_owner='sourav664', repo_name='real-estate-hybrid-app', mlflow=True)


# set the mlflow tracking server
import mlflow
mlflow.set_tracking_uri("https://dagshub.com/sourav664/real-estate-hybrid-app.mlflow")


def load_model_information(file_path):
    with open(file_path, 'r') as f:
        run_info = json.load(f)
    return run_info



if __name__ == "__main__":
    
    #root path
    root_path = Path(__file__).parent.parent.parent
    
    # run information file path
    run_info_path = root_path / "run_information.json"
    
    
    # register the model
    run_info = load_model_information(run_info_path)
    
    
    # get the run id
    run_id = run_info["run_id"]
    model_name = run_info['model_name']
    
    
    # model to register path
    model_registry_path = f"runs:/{run_id}/{model_name}"
    
    
    # register the model
    model_version = mlflow.register_model(model_uri=model_registry_path,
                                          name=model_name)
    
    
    # get the model version
    registered_model_version = model_version.version
    registered_model_name = model_version.name
    logger.info(f"The latest model version in model registry is {registered_model_version}")
    
    
    # update the stage of the model to staging
    client = MlflowClient()
    client.transition_model_version_stage(
        name = registered_model_name,
        version = registered_model_version,
        stage = "Staging"
    )
    
    logger.info("Model pushed to Staging stage")

