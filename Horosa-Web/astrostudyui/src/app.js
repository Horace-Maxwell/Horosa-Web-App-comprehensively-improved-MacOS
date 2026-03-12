import { handleError } from './utils/helper';

if (typeof window !== 'undefined' && typeof EventTarget !== 'undefined') {
    const proto = EventTarget.prototype;
    const addEventListener = proto && proto.addEventListener;
    if (addEventListener && !window.__horosaDomNodeInsertedPatched) {
        proto.addEventListener = function(type, listener, options) {
            if (type === 'DOMNodeInserted') {
                return;
            }
            return addEventListener.call(this, type, listener, options);
        };
        window.__horosaDomNodeInsertedPatched = true;
    }
}


export const dva = {
    config: {
        onError(err) {
            console.log(err);
            handleError(err);
        },
    },
}
