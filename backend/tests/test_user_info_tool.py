import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools.user_info_tool import UserInfoTool

class DummyState(dict):
    pass

class DummyContext:
    def __init__(self):
        self.state = DummyState()

def test_learn_stores_raw():
    tool = UserInfoTool()
    ctx = DummyContext()
    res = tool.learn_about_user(ctx, "I love hiking")
    assert res["status"] in {"stored", "learned"}
    assert "facts._raw" in ctx.state and ctx.state["facts._raw"][-1] == "I love hiking"


def test_extract_my_is_pattern():
    tool = UserInfoTool()
    ctx = DummyContext()
    res = tool.learn_about_user(ctx, "My favorite color is blue")
    assert res["status"] == "learned"
    assert res["extracted"]["favorite_color"] == "blue"
    assert "favorite_color" in ctx.state


def test_extract_role():
    tool = UserInfoTool()
    ctx = DummyContext()
    res = tool.learn_about_user(ctx, "I am a software engineer")
    assert res["status"] == "learned"
    assert res["extracted"]["role"] == "a software engineer"
    assert ctx.state["role"] == "a software engineer"
