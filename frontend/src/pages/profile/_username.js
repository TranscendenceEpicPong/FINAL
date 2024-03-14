import {html} from "../../html.js";
import { getProfile } from "../../utils/profile.js";

export default async ({ username }) => {
    const profile = await getProfile(username);
    console.log(profile.games);
    if (profile.status === 401)
        return html`<h1>Unauthorized</h1>`;
    if (profile.status === 404)
        return html`<profile-not-found></profile-not-found>`;
    return html`
        <profile-container
            username="${profile.username}"
            avatar="${profile.avatar}"
            wins="${`${profile.wins}`}"
            loses="${`${profile.loses}`}"
            games="${JSON.stringify(profile.games)}"
        ></profile-container>
    `
}
