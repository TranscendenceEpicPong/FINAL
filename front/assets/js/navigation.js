document.addEventListener('DOMContentLoaded', () => {
	document.querySelectorAll('a').forEach(link => {
		link.addEventListener('click', (e) => {
			e.preventDefault();
			navigateTo(link.getAttribute('href'));
		});
	});
});

function isAuthPage(page)
{
	return page.startsWith('#authentication');
}

function getLocation(page)
{
	if (page.startsWith('http://localhost/'))
		page = page.replace('http://localhost/', '');
	if (page.startsWith('#'))
		page = page.substring(1);
	if (!page.length)
		page = '/home';
	return page;
}

function hideAllPage()
{
	var pages = document.querySelectorAll('[data-bs-page]');
	for (var i = 0; i < pages.length; i++) {
		pages[i].style.display = 'none';
	}

	var subpages = document.querySelectorAll('[data-bs-sub-page]');
	for (var i = 0; i < subpages.length; i++) {
		subpages[i].style.display = 'none';
	}
}

function navigateTo(link)
{
	hideAllPage();
	if (link.startsWith('/'))
		link = link.substring(1);
	if (!link.length)
		link = 'home';
	const parts = link.split('/');
	parts.forEach((part, i, parts) => {
		const tmp = link.split('/', i + 1).join('/');
		const page = document.querySelector(`[data-bs-page="${tmp}"]`);
		page.style.display = 'block';
	});
	window.location.href = `#${link}`;
	// if (!page)
	// 	window.history.pushState({ page: 'notFound' }, '', `/not-found`);
	// if (!window.location.pathname.endsWith(`/${link}`)) {
	// 	window.history.pushState({ page: link }, '', `/${link}`);
	// }
}
