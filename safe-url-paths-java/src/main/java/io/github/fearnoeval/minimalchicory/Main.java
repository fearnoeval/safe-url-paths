package io.github.fearnoeval.minimalchicory;

import java.util.List;

public class Main {
    public static void main(String[] _args) {
        final var staticsAndDynamics = List.of(
            new Context(
                List.of("/items/foo/", "/name"),
                List.of("42")
            ),
            new Context(
                List.of("/user/", "/items/", ""),
                List.of("123", "some/characters/../should be/escaped")
            )
        );

        for (final var ctx : staticsAndDynamics) {
            final var statics = ctx.statics();
            final var dynamics = ctx.dynamics();

            final var interpolator = PathInterpolator.defaultImplementation(statics);

            System.out.println("Interpolating " + dynamics + " into " + statics);

            final var result = interpolator.interpolate(dynamics);

            System.out.println("Result: " + result);
        }
    }
}

record Context(
    List<String> statics,
    List<String> dynamics
) {}
