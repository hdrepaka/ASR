Hello All,

This is Automatic speec recognition project comprising three features such as Uplaod Audio file, Live recorded Audio trascription and Live captioning.

> Inorder to use this project one must downlaod the model from https://drive.google.com/drive/folders/1Fm_3s75sFCOYBh6nk4jYWZlziJlIrSV8?usp=drive_link.

Please use following stesp to use the project
1. Git clone this project
2. Now keep the above down loaded folder in same project folder
3. Open the project in VSCode > Go to Terminal
4. Install anaconda
5. Check the version by using comamnd conda --version
6. Create conda environment by using command conda create --name <EnvironmentName>
7. Initiate the conda Environment just created by using conda --init
8. Activate Conda Environment by using command conda activate Dev
     - This will start the enviroment
9. Now Run the fastapi server in above environment by using the command uvicorn Test:app --reload
     - This will start the fast api server and all our fast api servers are ready to use now
10. To Test the APIs using local server path such as http://127.0.0.1:8000/docs in browser URL
