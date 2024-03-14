import {html} from "../../html.js";
import { loadPage } from "../../router.js";
import {getData} from "../../store.js";

export default async ({ username }) => {
    const friend = getData('friends.active').find(friend => {
        return friend.receiver.username === username
    });
    console.log(friend);
    if (!friend)
        return html`<chats-friend-not-found></chats-friend-not-found>`;
    return html`
        <chats-container username="${friend.receiver.username}" avatar="${friend.receiver.avatar}"></chats-container>
    `
}