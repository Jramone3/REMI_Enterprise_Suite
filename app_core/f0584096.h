s to the miter point.
        if (abs(edgeID) == 2 && %s) {
            strokeOutset *= miter_extent(cosTheta, JOIN_TYPE/*miterLimit*/);
        }