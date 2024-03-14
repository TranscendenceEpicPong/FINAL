import {html} from "../../html.js";
import {postData} from "../../api.js";
import { getData, setData } from "../../store.js";

export default () => {
    return {
        template: html`
            <form id="form-update-profile" style="color: #aaaaaa;">
                <div>
                    <div>
                        <canvas id="avatar_preview" width="75" height="75" style="border: 1px solid white;"></canvas>
                    </div>
                    <label for="avatar">Avatar</label>
                    <input type="file" id="avatar" class="form-control" accept=".jpg, .jpeg, .png"/>
                    <input type="hidden" name="avatar" id="edit-profile-avatar-base64" class="form-control"/>
                </div>
                <div>
                    <label for="username">Nom d'utilisateur</label>
                    <input type="text" name="username" id="edit-profile-username" value="${getData('auth.user.username')}" class="form-control" required/>
                </div>
                <div>
                    <label for="password">Mot de passe</label>
                    <input type="password" name="password" id="edit-profile-password" class="form-control" />
                </div>
                <div>
                    <label for="confirm_password">Confirmation</label>
                    <input type="password" name="confirm_password" id="edit-profile-confirm_password" class="form-control" />
                </div>
                <div class="mt-3">
                    <button type="submit" class="btn btn-primary">Mettre à jour</button>&nbsp;<nav-link href="/edit-2fa">${getData('auth.user.a2f_enabled') ? 'Désactiver' : 'Activer'} la 2fa</nav-link>
                </div>
            </form>
        `,
        handlers: [
            {
                selector: "form",
                event: "submit",
                method: (e) => {
                    console.log(e);
                    const avatar = document.getElementById('edit-profile-avatar-base64').value;
                    const username = document.getElementById('edit-profile-username').value;
                    const password = document.getElementById('edit-profile-password').value;
                    const confirm_password = document.getElementById('edit-profile-confirm_password').value;

                    postData(
                        `${process.env.BASE_URL}/me/update`,
                        {
                            avatar,
                            username,
                            password,
                            confirm_password
                        },
                        "PATCH"
                    ).then((data) => {
                        setData({
                            auth: {
                                user: data
                            }
                        });
                    }).catch((err) => {
                        let error = '';
                        console.error(err)
                        for (const [key, value] of Object.entries(err)) {
                            error += `${value}\n`;
                        }
                        showToast(error);
                    })
                }
            },
            {
                selector: 'input[type="file"]',
                event: "change",
                method: (e) => {
                    const file = e.target.files[0];
                    const reader = new FileReader();
                    reader.onloadend = function () {
                        const canvas = document.getElementById('avatar_preview');
                        const context = canvas.getContext('2d');
                        const original_image = new Image();
                        const resized_image = new Image();
                        original_image.src = reader.result;
                        original_image.onload = function () {
                            context.drawImage(original_image, 0, 0, 75, 75);
                            const dataURL = canvas.toDataURL('image/png');
                            document.getElementById('edit-profile-avatar-base64').value = dataURL;
                            resized_image.src = dataURL;
                        }
                    }
                    reader.readAsDataURL(file);
                }
            }
        ],

    }
}