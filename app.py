import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Remove this in production!

from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app, jsonify, send_from_directory
from flask_discord import DiscordOAuth2Session, Unauthorized
from flask_login import LoginManager, login_required, current_user, UserMixin, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from dotenv import load_dotenv
import requests
from flask_cors import CORS

load_dotenv()

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY') or 'your-secret-key'  # Replace with a real secret key in production
app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI")
app.config["DISCORD_BOT_TOKEN"] = os.getenv("DISCORD_BOT_TOKEN")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

discord = DiscordOAuth2Session(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the login route

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    bot_settings = db.relationship('BotSettings', backref='user', uselist=False)

class BotSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    server_id = db.Column(db.String(20), nullable=False)
    system_instructions = db.Column(db.Text, nullable=True)
    bot_prefix = db.Column(db.String(5), nullable=True)
    bot_nickname = db.Column(db.String(32), nullable=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'server_id', name='_user_server_uc'),)

# Forms
class BotSettingsForm(FlaskForm):
    system_instructions = TextAreaField('System Instructions', validators=[DataRequired()])
    bot_prefix = StringField('Bot Prefix', validators=[DataRequired(), Length(max=5)])
    bot_nickname = StringField('Bot Nickname', validators=[DataRequired(), Length(max=32)])
    submit = SubmitField('Save Changes')

@app.route("/")
def index():
    if current_user.is_authenticated:
        logger.info(f"Authenticated user accessing index: {current_user.username}")
        return redirect(url_for('settings'))
    else:
        logger.info("Unauthenticated user accessing index")
        return render_template('index.html')

@app.route("/login")
def login():
    logger.debug("Login route accessed")
    try:
        return discord.create_session(scope=['identify', 'guilds'])
    except Exception as e:
        logger.error(f"Error creating Discord session: {str(e)}", exc_info=True)
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("index"))

@app.route('/auth/callback')
def callback():
    try:
        discord.callback()
        user = discord.fetch_user()
        
        # Store the access token in the session
        session['discord_access_token'] = discord.get_authorization_token()['access_token']
        
        # Construct the avatar URL
        avatar_hash = user.avatar_hash
        avatar_url = f"https://cdn.discordapp.com/avatars/{user.id}/{avatar_hash}.png" if avatar_hash else None

        db_user = User.query.filter_by(discord_id=str(user.id)).first()
        if not db_user:
            db_user = User(
                discord_id=str(user.id),
                username=user.name,
                avatar_url=avatar_url
            )
            db.session.add(db_user)
        else:
            # Update existing user data
            db_user.username = user.name
            db_user.avatar_url = avatar_url
        
        db.session.commit()
        
        login_user(db_user)
        
        return redirect(url_for('settings'))
    except Unauthorized:
        return redirect(url_for("login"))
    except Exception as e:
        logger.error(f"An error occurred during callback: {str(e)}", exc_info=True)
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("index"))

@app.route('/api/get_user_servers')
@login_required
def get_user_servers():
    access_token = session.get('discord_access_token')
    if not access_token:
        return jsonify({'error': 'No access token provided'}), 400

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        # Fetch user's guilds from Discord API
        response = requests.get('https://discord.com/api/users/@me/guilds', headers=headers)
        response.raise_for_status()
        guilds = response.json()

        # Filter guilds where user has MANAGE_GUILD permission
        managed_guilds = [
            {
                'id': guild['id'],
                'name': guild['name'],
                'icon': f"https://cdn.discordapp.com/icons/{guild['id']}/{guild['icon']}.png" if guild['icon'] else None
            }
            for guild in guilds if (int(guild['permissions']) & 0x20) == 0x20
        ]

        return jsonify(managed_guilds)

    except requests.RequestException as e:
        app.logger.error(f"Error fetching user servers: {str(e)}")
        return jsonify({'error': 'Failed to fetch servers'}), 500

@app.route('/dashboard/settings')
@login_required
def settings():
    form = BotSettingsForm()
    access_token = session.get('discord_access_token')
    print(f"Access token in settings route: {access_token}")  # Debug print
    return render_template('bot_settings.html', form=form, access_token=access_token)

@app.route('/dashboard/settings/<string:server_id>', methods=['GET', 'POST'])
@login_required
def server_settings(server_id):
    form = BotSettingsForm()
    if form.validate_on_submit():
        settings = BotSettings.query.filter_by(user_id=current_user.id, server_id=server_id).first()
        if settings is None:
            settings = BotSettings(user_id=current_user.id, server_id=server_id)
            db.session.add(settings)
        settings.system_instructions = form.system_instructions.data
        settings.bot_prefix = form.bot_prefix.data
        settings.bot_nickname = form.bot_nickname.data
        db.session.commit()
        flash('Bot settings updated successfully!', 'success')
        return redirect(url_for('server_settings', server_id=server_id))
    elif request.method == 'GET':
        settings = BotSettings.query.filter_by(user_id=current_user.id, server_id=server_id).first()
        if settings:
            form.system_instructions.data = settings.system_instructions
            form.bot_prefix.data = settings.bot_prefix
            form.bot_nickname.data = settings.bot_nickname
    return render_template('bot_settings.html', form=form, server_id=server_id, access_token=session.get('discord_access_token'))

@app.route('/dashboard/knowledgebase')
@login_required
def knowledgebase():
    return render_template('knowledgebase.html')

@app.route('/dashboard/knowledgebase/create', methods=['GET', 'POST'])
@login_required
def create_knowledge_entry():
    # Implement the logic for creating knowledge entries here
    return render_template('create_knowledge_entry.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

def main():
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()