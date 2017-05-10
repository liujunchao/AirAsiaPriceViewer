from ghost import Ghost
ghost = Ghost()
page, extra_resources = ghost.open("http://xiaorui.cc")
assert page.http_status==200 and 'xiaorui' in ghost.content