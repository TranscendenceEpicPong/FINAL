import {html} from "../../html.js";
import { loadPage } from "../../router.js";
import { getData } from "../../store.js";
import { initAccess } from "../../utils/profile.js";

export default async () => {
    const response = await fetch(`${process.env.BASE_URL}/authentication/42-register/?code=${getData('auth_42.code')}`, {
        credentials: "include",
        mode: "cors",
    })
    .then(response => {
        if (response.ok)
            return setTimeout(async () => await initAccess('/'), 1000);
    });
    return html`
		<div style="background: #252a2f; color: #aaaaaa; position: absolute; top: 0; bottom: 0; left: 0; right: 0; height: 100%; width: 100%;" id="mainContainer">
            <div class="container pt-4">
                <h1>Connexion en cours</h1>
            </div>
        </div>
    `
}