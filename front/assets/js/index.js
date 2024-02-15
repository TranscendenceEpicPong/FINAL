document.addEventListener('DOMContentLoaded', async () => {
	hideAllPage();
	await loadProfile();
});

document.querySelectorAll('a').forEach(link => {
	// link.addEventListener('click', (e) => {
	// 	e.preventDefault();
	// 	const type = e.target.getAttribute('data-bs-type');
	// 	if (type === 'page')
	// 		showPage(e.target.getAttribute('href'));
	// 	else if (type === 'subpage')
	// 		showSubPage(e.target.getAttribute('href'));
	// });
})

function showPage(page)
{
	page = page.replace('http://localhost/', '');
	if (page.startsWith('/'))
		page = page.substring(1);
	console.log(page);
	document.querySelectorAll('[data-bs-page]').forEach(_ => {
		console.log(_.getAttribute('data-bs-page'));
		const is_this_page = _.getAttribute('data-bs-page') === page;
		_.style.display = is_this_page ? 'block' : 'none';
	})
}

function showSubPage(page)
{
	page = page.replace('http://localhost/', '');
	if (page.startsWith('/'))
		page = page.substring(1);
	console.log(page);
	document.querySelectorAll('[data-bs-sub-page]').forEach(_ => {
		const is_this_page = _.getAttribute('data-bs-sub-page') === page;
		_.style.display = is_this_page ? 'block' : 'none';
	})
}
