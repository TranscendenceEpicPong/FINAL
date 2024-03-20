import {html} from "../../html.js";
import { getData } from "../../store.js";
import {initAuth} from "../../auth.js";
import {loadPage} from "../../router.js";

export default async () => {
    console.log("42 REGISTER")
    const response = fetch(`${process.env.BASE_URL}/authentication/42-register/?code=${getData('auth_42.code')}`, {
        credentials: "include",
        mode: "cors",
    })
    .then(async (response) => {
        console.log(response)
        if (response.ok) {
            await initAuth();
            return setTimeout(async () => await loadPage('/'), 1000);
        }
    });
    return html`
		<div style="background: #252a2f; color: #ffffff; display: flex; justify-content: center; align-items: center;height:100svh;">
            <div class="text-center">
                <div class="spinner-grow bg-white mb-3" style="width: 3rem; height: 3rem;" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
                <h5>Connexion en cours...</h5>
            </div>
        </div>
    `
}