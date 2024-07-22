### environment variables setup

> create .env and .test.env files on the same lvl as .env.template and .test.env.template files respectively

> fill up .env file according .env.template

### .test.env requirements:
>  DB_NAME in .test.env must be equal to DB_TEST_NAME from .env

> the rest of the fields must be equally to .env for success connection to test database

---
### set up venv

python version: 3.10
> python3 -m venv venv

> . venv/bin/activate

> pip install -r requirements.txt

---
### create db 

> chmod +x init-multi-postgres-databases.sh

> docker-compose up 

---
### testing

> pytest

--- 

### init db for api main run (excluding testing)

> alembic upgrade head

> alembic revision --autogenerate -m "your msg"

> alembic upgrade head


### run api 
> python3 app/main.py

---

 

The project is written with FastAPI, FastAPIUsers, SQLAlchemy

db: alembic, postgresql, sqlalchemy, docker-compose



# Authentication
Using FastAPIUsers. 

## Sign Up
Endpoint: POST /auth

Description: Register a new user.

Request Body:

{
  "username": "string",
  "email": "string",
  "password": "string"
}

Response:

201 Created: Returns user details.


## Sign In
Endpoint: POST /auth/jwt

Description: Log in a user and receive a JWT token.

Request Body:

{
  "username": "string",
  "password": "string"
}

Response:

204 No Content


## Authenticated Route
Endpoint: GET /auth/authenticated_route

Description: Retrieve information about the currently authenticated user.

Response:

200 OK: Returns user details.

# Posts

## Get Posts

Endpoint: GET /users/{user-id}/posts/

Description: Retrieve posts by a specific user within a date range.

Query Parameters:

- start_date: (optional) Start date for filtering posts.
- end_date: (optional) End date for filtering posts.

Response:

200 OK: Returns a list of published posts.

204 No Content: No posts found.

404 Not Found: User does not exist

422 Validation Error: Authorization is required

## Get Specific Post

Endpoint: GET /users/{user_id}/posts/{post_id}

Description: Retrieve a specific post by ID.

Response:

200 OK: Returns post details.

403 Forbidden: Access to the post is blocked.

204 No Content: No posts found.

404 Not Found: User does not exist

422 Validation Error: Authorization is required

## Create Post

Endpoint: POST /users/{user-id}/posts/posts
Request Body:
{
  "content": "Hi",
  "auto_reply": true
}

#### Features:

- Content Moderation: Content is screened for inappropriate material using the Gemini model from Google API. If content is flagged, posts will not be visible in any lists. Users can modify the post content using the designated endpoint to resolve this.

- Auto-Reply: When users comment on a post, they will automatically receive a reply from the post owner, generated by the Gemini model.

Response:
201 Created: Returns post details

403 Forbidden: Content is blocked due to inappropriate content. 

403 Forbidden: Access to this post is not allowed for your user id

422 Validation Error: Authorization is required


## Update Post
Endpoint: PUT /users/{user_id}/posts/{post_id}

Description: Update an existing post.

Request Body:

{
  "content": "Hi",
  "auto_reply": true
}


#### Features:

- The is_blocked status is mutable depending on the updated content.

Response:
202 ACCEPTED: Returns post details

403 Forbidden: Content is blocked due to inappropriate content. 

422 Validation Error: Authorization is required

404 NOT FOUND: Post does not exist

## Delete Post
Endpoint: DELETE /users/{user_id}/posts/{post_id}

Description: Delete a specific post.

Response:

202 Accepted: Returns a success message.

422 Validation Error: Authorization is required

404 NOT FOUND: Post does not exist

403 Forbidden: Access to this post is not allowed for your user id


# Comments

## Create Comment
Endpoint: POST /users/{user_id}/posts/{post_id}/comments

Description: Add a comment to a specific post.

Request Body:
{
  "content": "Hi!"
}

#### Features:

- If Auto-Reply is enabled by the post owner, the user will receive an immediate response.
- Content Moderation: Content is screened for inappropriate material using the Gemini model from Google API. If content is flagged, posts will not be visible in any lists. Users can modify the post content using the designated endpoint to resolve this.
- Users can reply not only to posts but also to other comments by specifying the comment_id.

Response:
201 CREATED: Returns comment's data

422 Validation Error: Authorization is required

404 NOT FOUND: Post/User/Post by User/ does not exist

403 Forbidden: Content is blocked due to inappropriate content. 


## Update Comment
Endpoint: PATCH /users/{user_id}/posts/{post_id}/comments/{comment_id} 

Description: Update an existing comment. Accessible for comment owner. 

Request Body:
{
  "content": "string"
}


Response: 

201 CREATED: Returns comment's data

422 Validation Error: Authorization is required

404 NOT FOUND: Post/User/Post by User/ does not exist

403 Forbidden: Content is blocked due to inappropriate content. 


## Get All Comments for Post
Endpoint: GET /users/{user_id}/posts/{post_id}/comments 

Description: Retrieve all comments for a specific post within a date range. 


Response:

200 OK: Returns a list of comments.

204 NO CONTENT: There are no comment under this post

422 Validation Error: Authorization is required

404 NOT FOUND: Post/User/Post by User/ does not exist


## Get Comment
Endpoint: GET /users/{user_id}/posts/{post_id}/comments/{comment_id}

Description: Retrieve a specific comment by ID.

Response:

200 OK: Returns comment details.

404 NOT FOUND: Comment/Post/User/Post by User/ does not exist by specified ID

422 Validation Error: Authorization is required

## Delete Comment 
Endpoint: DELETE /users/{user_id}/posts/{post_id}/comments/{comment_id}

Description: Delete a specific comment. Accessible for comment owner and post owner.

Response:

202 Accepted: Returns a success message.

404 NOT FOUND: Post/User/Post by User/ does not exist

422 Validation Error: Authorization is required

403 FORBIDDEN: Access to this content is not allowed for your user id

# Breakdowns

## Comments Breakdowns
Endpoint: GET /api/comments-daily-breakdown

Description: Get all comments within a specified date range.

Response:

200 OK: Returns all comments with tying to an authorized user: 

---
{ \
"sent": {"blocked": [], "published": []},\
"received": {"blocked": [], "published": []} \
}




## Posts Breakdowns
Endpoint: GET /api/posts-daily-breakdown/user/me/

Description: Get all posts within a specified date range.

Response:

200 OK: Returns all posts from an authorized specific user by {"blocked": [], "published": []}