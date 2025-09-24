
from src.contexts.train_model.TrainModel import TrainModel
from src.contexts.train_model.TrainGenreModel import TrainGenreModel



class CronTrainModelApp:
    def start(self, *, hour, model_type="regression"):
        ########################
        print(f"start train model cron in hour: {hour}, model_type: {model_type}", flush=True)
        
        if model_type == "genre" or model_type == "classification":
            TrainGenreModel.entrenarModeloGenero()
        else:
            # Default to regression model
            TrainModel.entrenarModelo()
