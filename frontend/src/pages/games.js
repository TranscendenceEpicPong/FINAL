import {html} from "../html.js";

export default () => {
    return html`
        <div class="d-flex" style="background: #252a2f;" id="mainContainer">
            <nav-container></nav-container>
            <div class="flex-grow-1 d-flex flex-column">
                <menu-btn></menu-btn>
                <div id="game_container" class="flex-grow-1 d-flex justify-content-center align-items-center mt-3 mb-3">
                    <div class="container">
                        <div class="row justify-content-center">
                            <div class="col-md-4 d-flex align-items-stretch">
                                <div class="card text-white bg-dark mb-3 d-flex flex-column mx-auto" style="width: 20rem;">
                                    <img src="/assets/img/game.png" class="card-img-top p-3" alt="Local Game Icon" style="object-fit: contain;">
                                    <div class="card-body d-flex flex-column">
                                        <h5 class="card-title">Local</h5>
                                        <p class="card-text">1v1 sur le même navigateur (Historique non enregistré)</p>
                                        <nav-btn href="/games/local" class="mt-auto" style="btn btn-primary btn-block">Accéder</nav-btn>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 d-flex align-items-stretch">
                                <div class="card text-white bg-dark mb-3 d-flex flex-column mx-auto" style="width: 20rem;">
                                    <img src="/assets/img/game.png" class="card-img-top p-3" alt="Multiplayer Game Icon" style="object-fit: contain;">
                                    <div class="card-body d-flex flex-column">
                                        <h5 class="card-title">Multijoueur</h5>
                                        <p class="card-text">Affrontez des adversaires à travers le monde</p>
                                        <nav-btn href="/games/multiplayer" class="mt-auto" style="btn btn-primary btn-block">Accéder</nav-btn>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 d-flex align-items-stretch">
                                <div class="card text-white bg-dark mb-3 d-flex flex-column mx-auto" style="width: 20rem;">
                                    <img src="/assets/img/game.png" class="card-img-top p-3" alt="Tournaments Icon" style="object-fit: contain;">
                                    <div class="card-body d-flex flex-column">
                                        <h5 class="card-title">Tournois</h5>
                                        <p class="card-text">Entrez dans un nouveau mode vous permettant de jouer à plusieurs sur une même catégorie de partie</p>
                                        <nav-btn href="/tournaments" class="mt-auto" style="btn btn-primary btn-block">Accéder</nav-btn>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}
