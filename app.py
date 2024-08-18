from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)


def load_blog_posts():
    """
    Load blog posts from the JSON file.

    Returns:
        list: A list of blog posts. Returns an empty list if the file doesn't exist.
    """
    if os.path.exists("blog_posts.json"):
        with open("blog_posts.json", "r") as file:
            return json.load(file)
    return []


def save_blog_posts(posts):
    """
    Save the list of blog posts to the JSON file.

    Args:
        posts (list): A list of blog posts to save.
    """
    with open("blog_posts.json", "w") as file:
        json.dump(posts, file, indent=4)
    print("Blog posts saved:", posts)  # Debug


def fetch_post_by_id(post_id):
    """
    Fetch a specific blog post by its ID.

    Args:
        post_id (int): The ID of the blog post to fetch.

    Returns:
        dict or None: The blog post with the given ID if found, otherwise None.
    """
    blog_posts = load_blog_posts()
    for post in blog_posts:
        if post["id"] == post_id:
            return post
    return None


@app.route("/")
def index():
    """
    Render the index page with a list of blog posts.

    Returns:
        str: Rendered HTML of the index page.
    """
    blog_posts = load_blog_posts()
    return render_template("index.html", posts=blog_posts)


@app.route("/add", methods=["GET", "POST"])
def add():
    """
    Handle the creation of a new blog post.

    If the request method is POST, adds a new blog post to the list.
    If the request method is GET, renders the form to add a new blog post.

    Returns:
        str: Redirects to the index page after a successful POST request.
        str: Rendered HTML of the add page for GET requests.
    """
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        author = request.form.get(
            "author", "Anonymous"
        )  # Default to 'Anonymous' if not provided

        blog_posts = load_blog_posts()

        new_post = {
            "id": len(blog_posts) + 1,
            "title": title,
            "content": content,
            "author": author,
            "likes": 0,
        }

        blog_posts.append(new_post)
        save_blog_posts(blog_posts)

        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    """
    Handle the updating of an existing blog post.

    If the request method is POST, updates the blog post with the new data.
    If the request method is GET, renders the form to update the blog post.

    Args:
        post_id (int): The ID of the blog post to update.

    Returns:
        str: Redirects to the index page after a successful POST request.
        str: Rendered HTML of the update page for GET requests.
        tuple: ("Post not found", 404) if the post does not exist.
    """
    blog_posts = load_blog_posts()
    post = fetch_post_by_id(post_id)

    if post is None:
        return "Post not found", 404

    if request.method == "POST":
        # Find the index of the post to update
        post_index = next(
            (index for (index, p) in enumerate(blog_posts) if p["id"] == post_id), None
        )
        if post_index is not None:
            # Update the post with the new data
            blog_posts[post_index]["title"] = request.form.get("title", post["title"])
            blog_posts[post_index]["content"] = request.form.get(
                "content", post["content"]
            )
            blog_posts[post_index]["author"] = request.form.get(
                "author", post.get("author", "Anonymous")
            )

            save_blog_posts(blog_posts)

        return redirect(url_for("index"))

    return render_template("update.html", post=post)


@app.route("/delete/<int:post_id>", methods=["POST"])
def delete(post_id):
    """
    Handle the deletion of a blog post.

    Args:
        post_id (int): The ID of the blog post to delete.

    Returns:
        str: Redirects to the index page after successfully deleting the post.
    """
    blog_posts = load_blog_posts()
    blog_posts = [post for post in blog_posts if post["id"] != post_id]
    save_blog_posts(blog_posts)
    return redirect(url_for("index"))


@app.route("/like/<int:post_id>", methods=["POST"])
def like(post_id):
    """
    Handle the liking of a blog post.

    Args:
        post_id (int): The ID of the blog post to like.

    Returns:
        str: Redirects to the index page after successfully liking the post.
        tuple: ("Post not found", 404) if the post does not exist.
    """
    # Load the blog posts
    blog_posts = load_blog_posts()

    # Find the post with the given ID
    post = next((p for p in blog_posts if p["id"] == post_id), None)

    if post is None:
        # Return a 404 response if the post is not found
        return "Post not found", 404

    # Increment the like count
    if "likes" in post:
        post["likes"] += 1
    else:
        post["likes"] = 1

    # Save the updated blog posts list
    save_blog_posts(blog_posts)

    # Redirect to the index page
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
