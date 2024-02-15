function getCookies()
{
	return document.cookie.split(';');
}

function getCookie(name)
{
	for (const cookie of getCookies())
	{
		const parts = cookie.split('=');
		if (parts.length === 2 && parts[0].trim() === name)
			return parts[1].trim();
	}
	return undefined;
}

function clear()
{
	document.cookie = '';
}