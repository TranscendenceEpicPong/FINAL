document.addEventListener('DOMContentLoaded', () => {
	document.querySelector('#form-edit-profile').
	addEventListener('submit', async (e) => {
		e.preventDefault();
		await fetch('/api/me/update', {
			method: 'PATCH',
			credentials: 'include',
			body: JSON.stringify({
				username: document.getElementById('profile-username').value,
				avatar: document.getElementById('profile-avatar').value,
				password: document.getElementById('profile-password').value,
				confirm_password: document.getElementById('profile-confirm_password').value,
			}),
		}).then(async (response) => {
			response = await response.json();
			if (response.status === 401)
				return navigateTo('/authentication/login');
			if (response.status >= 500 && response.status < 600)
				return console.error('Contactez un administrateur');
			if (response.status !== 200 && response.status && response.message)
				return alert(response.message)
			setUser(response);
			alert('Mise à jour réussi');
			// navigateTo('/home');
		
		})
	})
});

function getUser()
{
	return JSON.parse(localStorage.getItem('user'));
}

function setUser(_user)
{
	localStorage.setItem('user', JSON.stringify(_user));
	document.getElementById('profile-username').value = _user.username;
	document.getElementById('profile-avatar').value = _user.avatar;
}

async function deleteProfile()
{
	await fetch('/api/me/delete', {
		method: 'DELETE',
		credentials: 'include',
	}).then(async (response) => {
		response = await response.json();
		if (response.status === 401)
			return navigateTo('/authentication/login');
		if (response.status >= 500 && response.status < 600)
			return console.error('Contactez un administrateur');
		if (response.status !== 200 && response.status && response.message)
			return alert(response.message)
		localStorage.removeItem('user');
		navigateTo('/authentication/login');
	});
}

async function loadProfile()
{
	let success = false;
	await fetch('http://localhost/api/me', {
		method: 'GET',
		credentials: 'include',
	})
	.then(async (result) => {
		if (result.status === 401)
			return navigateTo('/authentication/login');
		if (result.status >= 500 && result.status < 600)
			return console.error('Erreur serveur');
		setUser(await result.json());
		const location = getLocation(window.location.href);
		success = true;
		return navigateTo(isAuthPage(location) ? '/home' : location);
	}).catch((err) => {});
	if (success)
		await setTimeout(initializeSocket(), 1000);
}

function isCurrentUsername(username)
{
	return getUsername() === username;
}

function getUsername()
{
	return getUser().username;
}