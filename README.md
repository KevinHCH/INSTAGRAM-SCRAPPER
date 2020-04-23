# Instagram scrapper
> This script catch all URL images from a user and stores in a Mongo Database
> Objeitve: Maybe create your own users API
### Requirements
- Docker 19.03 >=
- Python3
- Pip3
- pipenv (module)
### Deploy
- Execute the `deploy.sh` script
- *Complete the `.env` file with your credentials(user, password)*
- If you have problems to execute the script, try to modify the `DRIVER_PATH` and the `BRAVE_BROWSER_PATH` 

### Execute
- `pipenv run python index.py`
- `pipenv run python index.py write`: Will create the `data/`folder and store all the data retrieved per user in a `.json` file. (Will store the data in MongoDB too)