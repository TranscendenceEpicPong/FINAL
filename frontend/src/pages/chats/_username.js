import {html} from "../../html.js";
import { loadPage } from "../../router.js";
import {getData} from "../../store.js";
import { isCurrentUser } from "../../utils/profile.js";

export default async ({ username }) => {
    const friend = getData('friends.active').find(friend => {
        if (isCurrentUser(friend.sender.username))
            return friend.receiver.username === username
        return friend.sender.username === username;
    });
    console.log(friend);
    if (!friend)
        return html`<chats-friend-not-found></chats-friend-not-found>`;

    if (isCurrentUser(friend.sender.username))
        return html`
            <chats-container username="${friend.receiver.username}" avatar="${friend.receiver.avatar}"></chats-container>
        `
    return html`
        <chats-container username="${friend.sender.username}" avatar="${friend.sender.avatar}"></chats-container>
    `
}