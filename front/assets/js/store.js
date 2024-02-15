const getUser = () => JSON.parse(localStorage.getItem('user'));
const setUser = (_user) => {
	localStorage.setItem('user', JSON.stringify(_user));

	document.getElementById('profile-username').innerText = _user.username;
}
