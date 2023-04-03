export const funcInitialState = () => {
    return {
        mode: undefined,
        step: 0,
        sliderStep: 0,
        nextRenderTime: 0,
        isPlaying: true,
        isSliding: false,
        cache: [],
        initMessage: {
            mapSize: undefined,
            totalStep: undefined,
            bagVolume: undefined,
            allItemData: undefined,
        },
        focusPlayerId: undefined,
    }
}

const clipStep = (state, step) => {return Math.max(Math.min(step, state.cache.length - 1), 0)}

export function appReducer(state, action) {
    if (!state) {
        return funcInitialState()
    }
    switch (action.type) {
        case 'CONNECT_SERVER_BUTTON':
            return {...state, mode: state.mode ?? 'websocket'}
        case 'REPLAY_LOAD_BUTTON':
            return {...state, mode: state.mode ?? 'replay'}
        case 'UPDATE_REPLAY_DATA':
            return {
                ...state,
                initMessage: action.value.initMessage,
                cache: action.value.cache,
                nextRenderTime: Math.max(state.nextRenderTime, performance.now()),
            }
        case 'SLIDER_CHANGE':
            return {
                ...state,
                isSliding: true,
                sliderStep: clipStep(state, action.value),
                nextRenderTime: performance.now() + (state.isSliding ? 0 : 100),
            }
        case 'SLIDER_COMMIT':
            return {
                ...state,
                isSliding: false,
                sliderStep: clipStep(state, action.value),
                nextRenderTime: Math.max(state.nextRenderTime, performance.now()),
            }
        case 'STEP_INPUT':
            return {
                ...state,
                isPlaying: false,
                sliderStep: clipStep(state, action.value),
                nextRenderTime: Math.max(state.nextRenderTime, performance.now()),
            }
        case 'STEP_PREVIOUS':
            return {
                ...state,
                isPlaying: false,
                sliderStep: clipStep(state, state.sliderStep - 1),
                nextRenderTime: Math.max(state.nextRenderTime, performance.now()),
            }
        case 'STEP_NEXT':
            return {
                ...state,
                isPlaying: false,
                sliderStep: clipStep(state, state.sliderStep + 1),
                nextRenderTime: Math.max(state.nextRenderTime, performance.now()),
            }
        case 'STEP_FIRST':
            return {
                ...state,
                isPlaying: false,
                sliderStep: clipStep(state, 0),
                nextRenderTime: Math.max(state.nextRenderTime, performance.now()),
            }
        case 'STEP_LAST':
            return {
                ...state,
                isPlaying: false,
                sliderStep: clipStep(state, Infinity),
                nextRenderTime: Math.max(state.nextRenderTime, performance.now()),
            }
        case 'SWITCH_PLAYING':
            const isPlaying = !state.isPlaying
            return {
                ...state,
                isPlaying: isPlaying,
                nextRenderTime: Math.max(state.nextRenderTime, isPlaying ? performance.now() : -1)
            }
        case 'RECV_INIT_MESSAGE':
            return {
                ...state,
                initMessage: action.value,
            }    
        case 'RECV_DATA':
            return {
                ...state,
                cache: [...state.cache, action.value],
                nextRenderTime: Math.max(state.nextRenderTime, performance.now()),
            }
        case 'RENDER':
            const newStep = clipStep(state, state.step == state.sliderStep
                ? state.step + (state.isPlaying && !state.isSliding)
                : state.sliderStep)
            const nextRenderTime = state.step != newStep ? performance.now() + (state.isSliding ? 200 : 300) : -1
            return {
                ...state,
                step: newStep,
                sliderStep: newStep,
                nextRenderTime: Math.max(state.nextRenderTime, nextRenderTime)
            }
        case 'CLICK_PLAYER':
            return {...state, focusPlayerId: action.value}
    }
    throw Error('Unknown action: ' + action.type);
}