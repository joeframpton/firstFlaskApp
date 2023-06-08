## University Assignment to create a Flask app. 

This isn't intended to be a live site, but it serves to show an example of my work in Flask. I've sanitised the code to remove any passwords or secret keys. When the site was operational, it could only be accessed on Cardiff University's VPN. 

The site was an example of a personal website to showcase one's CV and skills. Most of the functionality could only be accessed by logging in. 

I've left the rest of this readme mostly as it was when I submitted this assignment. 



## Openshift URL:
[REMOVED]

## References:
The default profile picture is used with Creative Commons License and was sourced at: https://commons.wikimedia.org/wiki/File:Unknown_person.jpg

The stock profile picture is used with Creative Commons License and was sourced at: https://commons.wikimedia.org/wiki/File:Marvin_Terban_Bio_Photo.jpg


Many aspects were informed or adapted by the documentation:
- Flask: https://flask.palletsprojects.com/en/2.2.x/
- Flask SQLAlchemy: https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/
- Flask WTForms: https://flask-wtf.readthedocs.io/en/1.0.x/
- Jinja: https://jinja.palletsprojects.com/en/3.1.x/
- Flask-Login: https://flask-login.readthedocs.io/en/latest/


Many aspects of the HTML are adapted templates directly copied from Bootstrap. Their fonts & javascript library were utilised too.
https://getbootstrap.com/docs/5.3/getting-started/introduction/


jQuery was used to implement basic javascript functions:
https://jquery.com/


There were two youtubers whose guides were followed. While the code is different, it may resemble their architecture:
https://www.youtube.com/@prettyprinted

https://www.youtube.com/@Codemycom

There are additional inline references in the code.

## Using the site:
The default view of the site is aimed at recruiters or hiring managers. As such, their view is very limited. You can see the basic functionality on the home page and contact me page and the information that has been selected to be shown. 

#### Admin View:
To login, there is a discreet link in the copyright symbol in the footer. Or you could go to ~/login in the browser. (Most users won't need to login, so it was decided to leave out a clear link to the login page in the interest of minimalism)

Email address: testaccount@example.com

Password: password123

By logging in with these details, you will be able to see the full functionality of the site. To test the deleting admin function, I advise you make a new dummy account and delete that (as you won't be able to delete my primary admin account)

Please note: the contact me page sends an email to the current active user (i.e. John Smith as it is currently) and whoever's email is entered in the form. So please only enter email addresses you have access to or know are happy to be used for testing purposes.
