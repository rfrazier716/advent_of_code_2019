def gradient_descent_1D(error_function, error_function_args={},max_iterations=1000,x0=0,dx=1):
    # generator runs a gradient descent algorithm and returns the setpoint and error value
    #error function must use keyword inputs and the input has to be called "x"
    x=x0   #prime the input
    for j in range(max_iterations):
        error_function_args['x']=x  # update the input value
        error=error_function(**error_function_args)    # run error function
        error_function_args['x']=x-dx   # update input value so we can determine the gradient
        d_error=error-error_function(**error_function_args)
        yield x,error   # return the input and error before updating estimate
        x -= dx/d_error*error # update value of x for next estimate


def test_error_function(**kwargs):
    # test error function that is trying to get the input to be 7
    x=kwargs['x']
    return x-7

if __name__=="__main__":
    desc=gradient_descent_1D(test_error_function,dx=.1)
    tolerance=.1    # error tolerance acceptance criteria
    error=1 #initialize error so that it's larger than tolerance
    while abs(error)>tolerance:
        input,error=next(desc)
        print("input: {} \terror: {}".format(input,error))
    print("Input of {} produced acceptable result".format(input))