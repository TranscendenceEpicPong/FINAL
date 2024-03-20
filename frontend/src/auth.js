import {getUserInfo, postData, resetUserInfo} from "./api.js";
import {fetchMe, loadProfile} from "./utils/profile.js";
import {getData, resetStore, setData} from "./store.js";
import {resetSockets} from "./utils/socket.js";
import {loadPage} from "./router.js";

export async function initAuth()
{
    const { path, params } = getData('route');

    const set = (update) => setData(update, { reload: false });

    const user_info = getUserInfo();

    // Maybe not the best way to find it but seems to work
    const isOAuth2Flow = path === '/auth/42-register' && !!params['code']
    if (isOAuth2Flow) {
        // console.dir(user_info)
        if (user_info.loggedIn) {
            return '/';
        }
        await resetStore()
        set({ auth_42: params });
        return path;
    }

    if (!user_info.loggedIn) {
        return !['/auth/login', '/auth/register', '/auth/42-register'].includes(path) ?
                '/auth/login' : path
    }

    if (user_info.user.a2f_enabled && !user_info.user.a2f_verified) {
        console.dir("2FA", user_info)
        return '/auth/a2f'
    }

    const me = await fetchMe();
    if (!me) {
        set({auth: resetUserInfo()});
        return '/auth/login'
    }

    await loadProfile(me);

    return path
}

export async function logout()
{
    const res = await postData(`${process.env.BASE_URL}/authentication/logout`);
    resetSockets();
    console.dir(window.store)
    await resetStore();
    console.dir(window.store)
    return await loadPage("/auth/login");
}