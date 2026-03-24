/**
 * This class is intended to output content in a way that nothing is showed on the screen.
 * @author Meirav Levy
 */
class VoidRenderer implements Renderer{
     /**
      * Constructor.
      */
     public VoidRenderer() {}

     /**
      * doesn't print anything to the console.
      * @param board the board to render.
      */
     public void renderBoard(Board board) {}
}
