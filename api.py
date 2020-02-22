from flask_restful import Resource
from flask_httpauth import HTTPTokenAuth
from werkzeug.security import check_password_hash

from exts import db
from models import User, Game, GamePost, ApiToken, Article
from flask import jsonify, abort, request, session
import json

auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
    "secret-token-1": "John",
    "secret-token-2": "Susan"
}


@auth.verify_token
def verify_token(token):
    api_token = ApiToken.query.filter(ApiToken.token == token).first()
    if api_token:
        return True
    return False


def serialize(model):
    from sqlalchemy.orm import class_mapper
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return dict((c, getattr(model, c)) for c in columns)


class PublicGameList(Resource):
    decorators = [auth.login_required]
    """Public games list info"""

    def get(self):
        """Get public games list
                Args:
                    None
                Returns:
                    gamelist(json):
                        game_id (int)
                        game (json)
        """
        games = Game.query.filter(Game.state == 'Open').all()
        games_dict = {}
        for item in games:
            q_dict = serialize(item)
            games_dict[q_dict['game_id']] = q_dict
        return jsonify(games_dict)


class Games(Resource):
    """Games info"""
    def get(self, game_id):
        """Get game info
                Args:
                    game_id (int)

                Returns:
                    game(json):
                        author_id (int): 作者id
                        comment (str): 游戏简介
                        create_time (datetime): 创建时间
                        game_id (int): 游戏id
                        length (int): 游戏消息总数
                        member_limit (int): 人数上限
                        num_group (int): 频道数
                        num_member (int): 游戏人数
                        password (str): 密码
                        title (str): 游戏标题
        """
        game = Game.query.filter(Game.game_id == game_id).first()
        if game:
            q_dict = serialize(game)
            return jsonify(q_dict)
        else:
            abort(404)

    def put(self, game_id):
        """Update game info
                Args:
                    game_id (int)
                    game (json)
                Returns:
                    None
        """
        if not request.get_json() or not 'title' in request.get_json():
            abort(400)
        game_info = request.get_json()
        game = Game.query.filter(Game.game_id == game_id).first()
        game.title = game_info['title']
        game.comment = game_info['comment']
        game.password = game_info['password']
        game.member_limit = game_info['member_limit']
        db.session.commit()
        return 201

    def delete(self, game_id):
        """Delete game
                Args:
                    game_id (int)
                Returns:
                    None
        """
        game = Game.query.filter(Game.game_id == game_id).first()
        db.session.delete(game)
        db.session.commit()
        return 201


class AddNewGame(Resource):
    """Add new game"""

    def post(self):
        """Create new game
                Args:
                    Game (json)
                Returns:
                    None
        """
        if not request.get_json() or not 'title' in request.get_json():
            abort(400)
        game_info = request.get_json()
        game = Game()
        game.title = game_info['title']
        game.comment = game_info['comment']
        game.password = game_info['password']
        game.member_limit = game_info['member_limit']
        if session.get('user_id'):
            game.author_id = session['user_id']
        else:
            game.author_id = 0

        db.session.add(game)
        db.session.commit()
        return 201


class GamePosts(Resource):
    """GamePosts info"""
    def get(self, game_id, group=1):
        """Get gameposts list
                Args:
                    game_id (int)
                    group (int)
                Returns:
                    GamePosts List(json):
        """
        game = Game.query.filter(Game.game_id == game_id).first()
        if game:
            post_list = GamePost.query.filter(GamePost.game_id == game_id, GamePost.group_id == group).order_by(
                GamePost.post_id.desc()).all()
            posts_dict = {}
            for item in post_list:
                q_dict = serialize(item)
                posts_dict[q_dict['post_id']] = q_dict
            return jsonify(posts_dict)
        else:
            abort(404)

    def post(self, game_id, group=1):
        """Create new gamepost
                Args:
                    game_id (int):
                    group (int):
                    gamepost (json):
                        content  (str)
                        speaker  (str)
                        send_to  (str)
                        author_id  (int)
                Returns:
                    pass
        """
        if not request.get_json() or not 'content' in request.get_json():
            abort(400)
        gamepost_info = request.get_json()
        gamepost = GamePost()
        gamepost.content = gamepost_info['content']
        gamepost.speaker = gamepost_info['speaker']
        gamepost.send_to = gamepost_info['send_to']
        gamepost.game_id = game_id
        gamepost.group_id = group
        gamepost.author_id = gamepost_info['author_id']
        db.session.add(gamepost)
        db.session.commit()
        return 201


class ArticleList(Resource):
    decorators = [auth.login_required]
    """Get Articles list info"""
    def get(self):
        """Get articles list
                Args:
                    None
                Returns:
                    article_list(json):
        """
        articles = Article.query.all()
        articles_dict = {}
        for item in articles:
            q_dict = serialize(item)
            articles_dict[q_dict['article_id']] = q_dict
        return jsonify(articles_dict)


class Articles(Resource):
    """Articles info"""
    def get(self, article_id):
        """Get article by article_id
                Args:
                    article_id (int)
                Returns:
                    article info(json):

        """
        article = Article.query.filter(Article.article_id == article_id).first()
        if article:
            q_dict = serialize(article)
            return jsonify(q_dict)
        else:
            abort(404)

    def put(self, article_id):
        """Update article by article_id
                Args:
                    article_id (int)
                    article info (json)
                Returns:

        """
        if not request.get_json() or not 'title' in request.get_json():
            abort(400)
        article_info = request.get_json()
        article = Article.query.filter(Article.article_id == article_id).first()
        article.title = article_info['title']
        article.content = article_info['content']
        db.session.commit()
        return 201

    def delete(self, article_id):
        """Delete article by article_id
                Args:
                    article_id (int)
                Returns:
                    None

        """
        article = Article.query.filter(Article.article_id == article_id).first()
        db.session.delete(article)
        db.session.commit()
        return 201


class AddNewArticle(Resource):
    """Add new article"""
    def post(self):
        """Create new article
                Args:
                    article (json)
                Returns:
                    None
        """
        if not request.get_json() or not 'title' in request.get_json():
            abort(400)
        article_info = request.get_json()
        article = Article()
        article.title = article_info['title']
        article.content = article_info['content']
        article.tag = article_info['tag']
        article.state = article_info['state']
        if session.get('user_id'):
            article.author_id = session['user_id']
        else:
            article.author_id = 1
        db.session.add(article)
        db.session.commit()
        return 201


class Users(Resource):
    decorators = [auth.login_required]
    """Users info"""
    def get(self, user_id):
        """Get user info
                Args:
                    user_id (int)

                Returns:
                    user(json):{'user_id': user_id, 'username':user.username,'email':user.email}
        """
        user = User.query.filter(User.user_id == user_id).first()
        if user:
            q_dict = serialize(user)
            return jsonify(q_dict)
        else:
            abort(404)

    def put(self, user_id):
        """update user info
                Args:
                    user (json):
                        username (str)
                        qq  (str)
                Returns:
                    pass
        """
        user = User.query.filter(User.user_id == user_id).first()
        if not request.get_json() or not 'title' in request.get_json():
            abort(400)
        user_info = request.get_json()
        user.username = user_info['username']
        user.qq = user_info['qq']
        db.session.commit()
        return 201

    def delete(self, user_id):
        user = User.query.filter(User.user_id == user_id).first()
        db.session.delete(user)
        db.session.commit()
        return 201