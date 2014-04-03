<html>
<head>
</head>
<body>
<div style="">
Hej {{name}}!

Vi undrar om du kan medverka på dessa datum.
{% for event in events %}
{{event.date}} {{event.name}}
{% endfor %}
</div>
</body>
</html>