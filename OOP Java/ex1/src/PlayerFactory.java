/**
 * A factory that builds players for a game.
 * @author Meirav Levy
 */
class PlayerFactory {

    /**
     * constructor.
     */
    public PlayerFactory() {}

    /**
     * creates a player object.
     * @param type the type of the player to be created.
     * @return player object.
     */
    public Player buildPlayer(String type) {
        Player player = null;
        switch (type) {
            case "human":
                player = new HumanPlayer();
                break;
            case "whatever":
                player = new WhateverPlayer();
                break;
            case "clever":
                player = new CleverPlayer();
                break;
            case "genius":
                player = new GeniusPlayer();
                break;
        }
        return player;
    }
}
