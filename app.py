from src.apps.cron_train_model_app.CronTrainModelApp import CronTrainModelApp
from src.apps.api_app.ApiApp import ApiApp

import argparse


def main():
    parser = argparse.ArgumentParser(
        prog='Apps',
        description='Define all apps',
        epilog='Define all apps'
    )
    parser.add_argument('-app', '--application', default=None, required=False)
    parser.add_argument('-r', '--range', default=None, required=False)
    parser.add_argument('-type', '--model-type', default="genre", required=False)

    args = parser.parse_args()

    app_name = args.application
    model_type = args.model_type
    print(f"\n\n 🏁 start app: {app_name}, model_type: {model_type}")

    


    if app_name == "TrainModel":
        Cron_Train_Model_App = CronTrainModelApp()
        
        Cron_Train_Model_App.start(
            hour=args.range,
            model_type="genre"
        )
        return


    
    if app_name == "ApiApp":
        api_app = ApiApp()
        api_app.start()
        return


if __name__ == "__main__":
    main()