function createButton(text, attrs = [])
{
	const button = document.createElement('button');
	for (const attr of attrs)
		if (attr.name && attr.value)
			button.setAttribute(attr.name, attr.value);
	button.innerText = text;
	return button;
}