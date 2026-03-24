package pepse.world;

import danogl.GameObject;
import danogl.components.ScheduledTask;
import danogl.components.Transition;
import danogl.util.Vector2;

import java.util.Random;

/**
 * A class representing the wind's behaviour in the game's world.
 * @author Meirav Levy
 */
public class WindBehaviour {

    /**
     * Constructor.
     */
    public WindBehaviour() {}

    /**
     * Apllies the wind effects on the specified game object.
     * @param obj The game object to move.
     */
    public static void applyWindEffects(GameObject obj) {
        float transitionTime = 3;

        float timeToWaitAngle = transitionObjAngle(obj, transitionTime);
        transitionObjWidth(obj, transitionTime, timeToWaitAngle * 5);
    }

    /*
     * Transitions the object's angle to create an affect that it is moving from side to side with the wind.
     */
    private static float transitionObjAngle(GameObject obj, float transitionTime) {
        float objAngle = obj.renderer().getRenderableAngle();
        Random random = new Random();
        float timeToWaitAngle = random.nextFloat();

        Runnable objAngleTransition = () ->
                new Transition<>(obj, (Float angle) -> obj.renderer().setRenderableAngle(angle),
                        objAngle, -objAngle,
                        Transition.LINEAR_INTERPOLATOR_FLOAT, transitionTime,
                        Transition.TransitionType.TRANSITION_BACK_AND_FORTH,
                        null);
        new ScheduledTask(obj, timeToWaitAngle, false, objAngleTransition);
        return timeToWaitAngle;
    }

    /*
     * transitions the game object's width.
     */
    private static void transitionObjWidth(GameObject obj, float transitionTime, float timeToWait) {
        float widthFactorChange = 5f / 6;
        Vector2 initialObjDimensions = new Vector2(obj.getDimensions());
        Runnable objWidthTransition = () -> new Transition<>(obj, obj::setDimensions,
                initialObjDimensions,
                Vector2.of(initialObjDimensions.x() * widthFactorChange, initialObjDimensions.y()),
                Transition.CUBIC_INTERPOLATOR_VECTOR, transitionTime,
                Transition.TransitionType.TRANSITION_BACK_AND_FORTH, null);

        new ScheduledTask(obj, timeToWait, false, objWidthTransition);
    }
}
