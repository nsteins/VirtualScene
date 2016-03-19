# VirtualScene

This project is an album recommendation system for items available on bandcamp.com. The web app is currently running at http://listen.maple.zone  If you enter the name of an album from bandcamp, it will display a carousel containing the most popular albums amongst users who own the initial album. You can listen to the albums using the embedded bandcamp player or click through to the appropriate album site and purchase the album through bandcamp. 

The project files consist of two separate parts: 
    a scrapy app that crawls bandcamp.com for album and user data and stores it in a postgres database 
    a flask app that provides a web interface for accessing album info and recommended albums from the postgres database
    

If you wanted to run this site yourself there are several steps you would need to take beyond just 'pip install -r requirements.txt' (which you should obviously do)

  - install and configure postgresql-9.5
  
  - put your postgresql login info into both flask/app/settings.py AND scrapy/bandcamp/settings.py
  
  - run the scrapy spider to populate the database with the info from bandcamp.com (you have to do this slowly so that you don't upset their servers, it will take a long time)
  
  - edit flask/config.py to input your SECRET KEY
  
  - download BxSlider from http://bxslider.com/ and put it in flask/app/static
  
  - you can deploy the flask app locally by calling flask/run.py, however if you wish to deploy it remotely, you will need to run a server like Apache and configure it to use the flask app using the WSGI module
