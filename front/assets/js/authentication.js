function registerComponent()
{
	document.getElementById('authentication-register').style.display = 'block';
	document.getElementById('authentication-login').style.display = 'none';
}

async function a2fRequestCode()
{
	await fetch('/api/authentication/2fa/request-code', {
		method: 'GET',
		credentials: 'include',
	})
	.then(async (result) => {
		if (result.status === 200)
		{
			const data = (await result.json()).message;
			img = document.getElementById('qrcode-2fa');
			img.src = data.qrcode;
			document.getElementById('secret-2fa').value = data.secret;
		}
		else
		{
			result = await result.json();
			if (result.message)
				alert(result.message);
		}
	});
}

async function disconnect()
{
	await fetch('/api/authentication/logout', {
		method: 'POST',
		credentials: 'include',
	})
	.then(async (result) => {
		if (result.status === 200)
		{
			document.getElementById('authentication-page').style.display = 'block';
			document.getElementById('main').style.display = 'none';
			window.location.href = '';
		}
		else
		{
			result = await result.json();
			if (result.message)
				alert(result.message);
		}
	});
}

document.addEventListener('DOMContentLoaded', async () => {
	const authenticationPage = document.getElementById('authentication-page');
	const main = document.getElementById('main');

	if (!getCookie('authorization'))
		authenticationPage.style.display = 'block';
	else
		main.style.display = 'block';

	const registerForm = document.getElementById('form-register');
	registerForm && registerForm.addEventListener('submit', async (e) => {
		e.preventDefault();
		await fetch('http://localhost/api/authentication/register', {
			method: 'POST',
			credentials: 'include',
			body: JSON.stringify({
				username: e.target.username.value,
				avatar: e.target.avatar.value,
				password: e.target.password.value,
				confirm_password: e.target.confirm_password.value,
			}),
		})
		.then(async (result) => {
			if (result.status === 200)
			{
				console.log('SUCCESSFULL REGISTRATION');
				await loadProfile();
				return navigateTo('/home');
			}
			console.log(await result.json());
		}).catch((err) => {
			console.log(err);
		});
	})

	const loginForm = document.getElementById('form-login');
	loginForm && loginForm.addEventListener('submit', async (e) => {
		e.preventDefault();
		await fetch('http://localhost/api/authentication/login', {
			method: 'POST',
			credentials: 'include',
			body: JSON.stringify({
				username: e.target.username.value,
				password: e.target.password.value,
				code: e.target.code.value,
			})
		})
		.then(async (result) => {
			if (result.status === 200)
			{
				authenticationPage.style.display = 'none';
				main.style.display = 'block';
				await loadProfile();
				return navigateTo('/home');
			}
			else
			{
				result = await result.json();
				if (result.message)
					alert(result.message);
			}
		}).catch((err) => {
			console.log(err);
		});
	})

	const formEnabling2fa = document.getElementById('form-enabling-a2f');
	formEnabling2fa && formEnabling2fa.addEventListener('submit', async (e) => {
		console.log('ACTIVATION 2FA');
		e.preventDefault();
		await fetch('http://localhost/api/authentication/2fa/enable', {
			method: 'POST',
			credentials: 'include',
			body: JSON.stringify({
				code: e.target.code.value,
			}),
		})
		.then(async (result) => {
			if (result.status === 200)
			{
				alert('SUCCESSFULL 2FA ENABLING');
			}
			else
			{
				result = await result.json();
				if (result.message)
					alert(result.message);
			}
		}).catch((err) => {
			console.log(err);
		});
	});
});
