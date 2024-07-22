import pytest
import http.cookies

from httpx import AsyncClient

from app.main import app
from .conftest import setup_db, fake, event_loop, user_json


@pytest.mark.asyncio
class TestUsersFlow:
    user_1_json = None
    user_2_json = None
    headers = {"Content-Type": "application/json"}

    @pytest.fixture()
    async def client(self):
        async with AsyncClient(app=app, base_url="http://localhost:3000") as client:
            yield client

    async def register_user(self, client, create_user_json, expected_status=201):
        response = await client.post(
            "/auth/auth/register", json=create_user_json, headers=self.headers
        )
        assert response.status_code == expected_status
        return response

    @staticmethod
    async def login_user(client, create_user_json):
        response = await client.post(
            "/auth/auth/jwt/login",
            data={"username": create_user_json["email"], "password": create_user_json["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 204

        cookie_jar = http.cookies.SimpleCookie()
        cookie_jar.load(response.headers.get("set-cookie"))
        cookies = {key: morsel.value for key, morsel in cookie_jar.items()}
        client.cookies.update(cookies)
        return response

    @staticmethod
    async def check_user(client, create_user_json):
        response = await client.get("/auth/authenticated-route", cookies=client.cookies.jar)
        assert response.status_code == 200
        assert create_user_json["email"] in response.json()["email"]

    async def create_post(self, client, user_id, post_json, expected_status=201):
        response = await client.post(
            f"/users/{user_id}/posts",
            json=post_json, headers=self.headers, follow_redirects=True, cookies=client.cookies.jar
        )
        assert response.status_code == expected_status
        return response

    async def get_post(self, client, user_id, post_id, expected_status=200):
        response = await client.get(
            f"/users/{user_id}/posts/{post_id}",
            headers=self.headers, follow_redirects=True, cookies=client.cookies.jar
        )

        assert response.status_code == expected_status
        return response

    async def get_posts(self, client, user_id, expected_status=200):
        response = await client.get(
            f"/users/{user_id}/posts",
            headers=self.headers, follow_redirects=True, cookies=client.cookies.jar
        )
        assert response.status_code == expected_status
        return response

    async def create_comment(
            self, client, user_id, post_id, comment_json, comment_id_reply_to=None, expected_status=201):
        url = f"/users/{user_id}/posts/{post_id}/comments/"
        if comment_id_reply_to:
            url = f"{url}?comment-id={comment_id_reply_to}"
        response = await client.post(
            url,
            json=comment_json, headers=self.headers, follow_redirects=True, cookies=client.cookies.jar
        )
        assert response.status_code == expected_status
        return response

    async def get_breakdown(self, client, breakdown_url, expected_status=200):
        response = await client.get(
            breakdown_url, headers=self.headers, follow_redirects=True, cookies=client.cookies.jar
        )
        assert response.status_code == expected_status
        return response

    @staticmethod
    async def get_reply_from_user(response, comment_id):
        received_comments = response.json().get("received").get("published")
        reply_from_user1 = next(
            (
                received_comment for received_comment in received_comments
                if received_comment["parent_comment"] and received_comment["parent_comment"]["id"] == comment_id
            ),
            None
        )
        return reply_from_user1

    async def update_post(self, client, user_id, post_id, post_json, expected_status=202):
        response = await client.put(
            f"/users/{user_id}/posts/{post_id}",
            headers=self.headers, follow_redirects=True,
            cookies=client.cookies.jar,
            json=post_json
        )
        assert response.status_code == expected_status
        return response

    async def delete_post(self, client, user_id, post_id, expected_status):
        response = await client.delete(
            f"/users/{user_id}/posts/{post_id}",
            headers=self.headers, follow_redirects=True, cookies=client.cookies.jar
        )
        assert response.status_code == expected_status
        return response

    async def update_comment(self, client, user_data, comment_id, comment_json, expected_status=202):
        response = await client.put(
            f"/users/{user_data['id']}/posts/{user_data['posts_ids'][0]}/comments/{comment_id}",
            json=comment_json,
            headers=self.headers,
            follow_redirects=True,
            cookies=client.cookies.jar
        )
        assert response.status_code == expected_status
        return response

    async def delete_comment(self, client, user_id, post_id, comment_id, expected_status):
        response = await client.delete(
            f"/users/{user_id}/posts/{post_id}/comments/{comment_id}",
            headers=self.headers, follow_redirects=True, cookies=client.cookies.jar
        )
        assert response.status_code == expected_status
        return response

    @pytest.mark.run(order=1)
    async def test_user1_flow(self, client, user_json):
        user1_json = user_json

        # Register and login user1
        response = await self.register_user(client, user1_json)
        user1_id = response.json()["id"]
        TestUsersFlow.user_1_json = {**user1_json, "id": user1_id}

        await self.register_user(client, user1_json, expected_status=400)
        await self.login_user(client, user1_json)
        await self.check_user(client, user1_json)

        # Create unblocked post
        post_json = {"content": fake.text(max_nb_chars=100), "auto_reply": True}
        response = await self.create_post(client, user1_id, post_json)
        post_id = response.json()["id"]
        TestUsersFlow.user_1_json["posts_ids"] = [post_id]
        assert response.json()["is_blocked"] is False

        # Create blocked post
        blocked_post_json = {"content": "Fuck off!", "auto_reply": True}
        response = await self.create_post(client, user1_id, blocked_post_json, expected_status=403)
        blocked_post_id = response.headers.get("content-id")

        # Get blocked current user's post
        response = await self.get_post(client, user1_id, blocked_post_id, expected_status=200)
        assert response.json()["is_blocked"] is True

        # Get all user's posts by user_id
        response = await self.get_posts(client, user1_id, expected_status=200)
        assert len(response.json()) == 1
        assert isinstance(response.json(), list)

        # Check posts breakdown
        await self.get_breakdown(client, f"/api/breakdowns/posts-daily-breakdown/user/me/")

        # Update blocked post
        response = await self.update_post(client, user1_id, blocked_post_id, post_json)
        assert response.json()["is_blocked"] is False

        response = await self.get_breakdown(client, f"/api/breakdowns/posts-daily-breakdown/user/me/")
        assert len(response.json().get("published")) == 2
        assert len(response.json().get("blocked")) == 0

        # Delete not existing post with not existing user-id
        response = await self.delete_post(client, user1_id + 1, blocked_post_id, expected_status=404)
        assert "not exist" in response.json()["detail"]

        # Delete post
        await self.delete_post(client, user1_id, blocked_post_id, expected_status=202)

        # Delete not existing post with existing user-id
        await self.delete_post(client, user1_id, blocked_post_id, expected_status=404)

        # Check no comments
        await self.get_breakdown(
            client, f"/api/breakdowns/comments-daily-breakdown/user/me/", expected_status=204
        )

        # Create comment
        comment_json = {"content": fake.text(max_nb_chars=40)}
        response = await self.create_comment(client, user1_id, post_id, comment_json)
        assert response.json()["id"] is not None

        # Check creation and not getting auto-reply
        response = await self.get_breakdown(client, f"/api/breakdowns/comments-daily-breakdown/user/me/")
        assert len(response.json().get("sent").get("published")) == 1
        assert len(response.json().get("received").get("published")) == 0

        # Log out user1
        response = await client.post("/auth/auth/jwt/logout")
        assert response.status_code == 204

        client.cookies.jar.clear()
        assert not client.cookies.jar

    @pytest.mark.run(order=2)
    async def test_user2_flow(self, client, user_json):
        user2_json = user_json

        # Register and login user2
        response = await self.register_user(client, user2_json)
        user2_id = response.json()["id"]

        assert user2_id is not None

        TestUsersFlow.user_2_json = {**user2_json, "id": user2_id}

        # register already existed user
        await self.register_user(client, user2_json, expected_status=400)

        await self.login_user(client, user2_json)
        await self.check_user(client, user2_json)

        # Create comment from user2 under user1's post
        comment_json = {"content": fake.text(max_nb_chars=40)}
        response = await self.create_comment(
            client, TestUsersFlow.user_1_json["id"], TestUsersFlow.user_1_json["posts_ids"][0], comment_json
        )

        assert response.json()["id"] is not None
        assert response.json()["comment_id_reply_to"] is None

        # Check comment auto-reply from user1
        comment_id = response.json()["id"]
        breakdown_url = f"/api/breakdowns/comments-daily-breakdown/user/me"

        response = await self.get_breakdown(client, breakdown_url)
        reply_from_user1 = await self.get_reply_from_user(response, comment_id)
        assert reply_from_user1 is not None

        # Create blocked comment from user2 under user1's post
        blocked_comment_json = {"content": "You're an idiot!"}
        response = await self.create_comment(
            client, TestUsersFlow.user_1_json["id"],
            TestUsersFlow.user_1_json["posts_ids"][0],
            blocked_comment_json, expected_status=403,
            comment_id_reply_to=reply_from_user1['id']
        )

        blocked_comment_id = response.headers.get("content-id")
        assert blocked_comment_id is not None

        # NOT to get auto-reply from user1 -- check by comments breakdown
        response = await self.get_breakdown(client, breakdown_url)
        reply_from_user1 = await self.get_reply_from_user(response, blocked_comment_id)

        assert reply_from_user1 is None

        # Update blocked comment from user2
        response = await self.update_comment(
            client, TestUsersFlow.user_1_json, blocked_comment_id, comment_json
        )
        assert response.json().get("id") is not None

        # Check comment auto-reply from user1 after update
        comment_id = response.json()["id"]
        response = await self.get_breakdown(client, breakdown_url)

        reply_from_user1 = await self.get_reply_from_user(response, comment_id)
        assert reply_from_user1 is not None

        # Delete comment from user2
        response = await self.delete_comment(
            client, TestUsersFlow.user_1_json["id"],
            TestUsersFlow.user_1_json["posts_ids"][0], blocked_comment_id, expected_status=202
        )
        assert f"{comment_id} deleted successfully" in response.json()["msg"]

        # Log out user2
        response = await client.post("/auth/auth/jwt/logout")
        assert response.status_code == 204
        client.cookies.jar.clear()
        assert not client.cookies.jar

