# Addnewarticle(Add new article)

## POST(Create new article)

#### url
- /addarticle

#### doc
```
                Args:
                    article (json)
                Returns:
                    None
```



# Addnewgame(Add new game)

## POST(Create new game)

#### url
- /addgame

#### doc
```
                Args:
                    Game (json)
                Returns:
                    None
```



# Articlelist

## GET(Get articles list)

#### url
- /articles/

#### doc
```
                Args:
                    None
                Returns:
                    article_list(json):
```



# Articles(Articles info)

## DELETE(Delete article by article_id)

#### url
- /articles/<article_id>

#### doc
```
                Args:
                    article_id (int)
                Returns:
                    None
```


## GET(Get article by article_id)

#### url
- /articles/<article_id>

#### doc
```
                Args:
                    article_id (int)
                Returns:
                    article info(json):
```


## PUT(Update article by article_id)

#### url
- /articles/<article_id>

#### doc
```
                Args:
                    article_id (int)
                    article info (json)
                Returns:
```



# Gameposts(GamePosts info)

## GET(Get gameposts list)

#### url
- /gameposts/<game_id>/<group>

#### doc
```
                Args:
                    game_id (int)
                    group (int)
                Returns:
                    GamePosts List(json):
```


## POST(Create new gamepost)

#### url
- /gameposts/<game_id>/<group>

#### doc
```
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
```



# Games(Games info)

## DELETE(Delete game)

#### url
- /games/<game_id>

#### doc
```
                Args:
                    game_id (int)
                Returns:
                    None
```


## GET(Get game info)

#### url
- /games/<game_id>

#### doc
```
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
```


## PUT(Update game info)

#### url
- /games/<game_id>

#### doc
```
                Args:
                    game_id (int)
                    game (json)
                Returns:
                    None
```



# Publicgamelist

## GET(Get public games list)

#### url
- /games/

#### doc
```
                Args:
                    None
                Returns:
                    gamelist(json):
                        game_id (int)
                        game (json)
```



# Users

## GET(Get user info)

#### url
- /users/<user_id>

#### doc
```
                Args:
                    user_id (int)

                Returns:
                    user(json):{'user_id': user_id, 'username':user.username,'email':user.email}
```


## POST(Register new user)

#### url
- /users/<user_id>

#### doc
```
                Args:
                    user (json):

                Returns:
                    pass
```


## PUT(update user info)

#### url
- /users/<user_id>

#### doc
```
                Args:
                    user (json):

                Returns:
                    pass
```



