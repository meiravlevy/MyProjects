/**
 * A factory that builds renderers
 * @author Meirav Levy
 */
class RendererFactory {

    /**
     * constructor.
     */
    public RendererFactory() {}

    /**
     * Creates a renderer object.
     * @param type the type of the renderer to be created.
     * @param size the size of the board to render.
     * @return a renderer object
     */
    public Renderer buildRenderer(String type, int size) {
        Renderer renderer = null;
        switch (type) {
            case "none":
                renderer = new VoidRenderer();
                break;
            case "console":
                renderer = new ConsoleRenderer(size);
                break;
        }
        return renderer;
    }
}
