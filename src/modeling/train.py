import pandas as pd
import numpy as np
import joblib
import logging
import yaml
from pathlib import Path
from sklearn.preprocessing import FunctionTransformer
from sklearn.compose import TransformedTargetRegressor
from lightgbm import LGBMRegressor

TARGET = 'price'

#create logger
logger = logging.getLogger("train_model")
logger.setLevel(logging.DEBUG)

# console handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# file handler
file_handler = logging.FileHandler('train_model.log')
file_handler.setLevel(logging.DEBUG)


# create a fomratter
formatter = logging.Formatter(fmt='[%(asctime)s] (line %(lineno)d) - %(name)s - %(levelname)s in %(module)s: %(message)s')
# add formatter to handler
handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# ADD BOTH HANDLERS
logger.addHandler(handler)
logger.addHandler(file_handler)


def load_data(data_path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(data_path)
        
    except FileNotFoundError:
        logger.error("The file to load does not exist")
        raise
        
    return df


def read_params(file_path):
    with open(file_path, 'r') as f:
        params_file = yaml.safe_load(f)
        
    return params_file

def save_model(model, save_dir: Path, model_name: str) -> None:
    # form the save location
    save_location = save_dir / model_name
    
    # save the model
    joblib.dump(value=model, filename=save_location)


def save_transformer(transformer, save_dir: Path, transformer_name: str) -> None:
    # form the save location
    save_location = save_dir / transformer_name
    
    # save the transformer
    joblib.dump(value=transformer, filename=save_location)
    
    
def train_model(model, X_train: pd.DataFrame, y_train):
    # fit the model
    model.fit(X_train, y_train)
    
    return model

def make_X_and_y(data: pd.DataFrame, target: str) -> tuple:
    X = data.drop(columns=[target])
    y = data[target]
    
    return X, y


if __name__ == "__main__":
    # root path
    root_path = Path(__file__).parent.parent.parent
    # params path
    params_file_path = root_path / "params.yaml"
    
        
    # data path
    train_transformed_path = root_path / "data" / "processed" / "train_trans.csv"
   
    
    # read the data
    train_transformed = load_data(train_transformed_path)
    logger.info("Training data read successfully")
    
    
    # split the transformed data
    X_train, y_train = make_X_and_y(train_transformed, TARGET)
    logger.info("Training data split successfully")
    
    
    # model parameters
    model_params = read_params(params_file_path)['Train']
    
    # light gbm params
    lgbm_params = model_params["LightGBM"]
    logger.info("Light GBM parameters read")
    lgbm = LGBMRegressor(**lgbm_params)
    logger.info("built Light GBM model")
    

    # log transformer
    log_transformer = FunctionTransformer(func=np.log1p, inverse_func=np.expm1, validate=True)
    logger.info("Target Transformer built")
    
    # make the model wrapper
    model = TransformedTargetRegressor(regressor=lgbm,
                                       transformer=log_transformer)
    logger.info("Model wrapper built")
    
    # fit the model on training data
    train_model(model, X_train, y_train)
    logger.info("Model trained on training data")
    
    # model filename
    model_filename = "model.joblib"
    
    # directory to save the model
    model_save_dir = root_path / "models"
    model_save_dir.mkdir(exist_ok=True)
    
    
    # extract the model from wrapper
    transformer = model.transformer_
    
    # save the model
    save_model(model=model,
            save_dir=model_save_dir,
            model_name=model_filename)
    logger.info("Trained model saved to location")
    
    
    # save the transformer
    transformer_filename = "log_transformer.joblib"
    transformer_save_dir = model_save_dir
    save_transformer(transformer=transformer,
                    save_dir=transformer_save_dir,
                    transformer_name=transformer_filename)
    logger.info("Target transformer saved to location")
    