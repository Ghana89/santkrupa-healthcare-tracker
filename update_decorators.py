with open('hospital/views.py', 'r') as f:
    content = f.read()
content = content.replace('@login_required\n', '@login_required(login_url="login")\n')
with open('hospital/views.py', 'w') as f:
    f.write(content)
print('Updated all @login_required decorators!')
