from project3.init import create_app
from project3.authen import auth


app = create_app()


if __name__ == '__main__':    
    app.run(debug=True) 