from isodate import parse_date, parse_duration
from functools import partial

from .functions.generic import FunctionRegistry
from .qname import QName, Parameter

reg = FunctionRegistry()

def fn_count(args):

    if isinstance(args, list):

        return len(args)
    else:
        return 1
    # if self.cast_args:
    #     # If arguments are already casted from parameters or paths, use this information
    #     return len(self.cast_args)
    #
    # else:
    #     # If casting has not been done, try to get the length of the arguments list.
    #
    #     try:
    #         return len(self.arguments)
    #     except TypeError:
    #         raise Exception("Run self.cast_parameters(paramlist) first")

def fn_avg(args):

    return sum(args) / len(args)
    # if self.cast_args:
    #     return sum(self.cast_args) / len(self.cast_args)
    #
    # else:
    #     try:
    #
    #         return sum(self.arguments) / len(self.arguments)
    #     except TypeError:
    #         raise Exception("Run self.cast_parameters(paramlist) first")


def fn_max(args):

    return max(args)
    # if self.cast_args:
    #     return max(self.cast_args)
    #
    # else:
    #     try:
    #
    #         return max(self.arguments)
    #     except TypeError:
    #         raise Exception("Run self.cast_parameters(paramlist) first")

def fn_min(args):
    return min(args)
    # if self.cast_args:
    #     return min(self.cast_args)
    #
    # else:
    #     try:
    #
    #         return min(self.arguments)
    #     except TypeError:
    #         raise Exception("Run self.cast_parameters(paramlist) first")

def fn_sum(args):
    return sum(args)
    # if self.cast_args:
    #     return sum(self.cast_args)
    #
    # else:
    #     try:
    #
    #         return sum(self.arguments)
    #     except TypeError:
    #         raise Exception("Run self.cast_parameters(paramlist) first")

def fn_not(args):
    for arg in args:
        if arg is True:
            return False  # found an argument that is true

    # Did not find a True value
    return True

    # if self.cast_args:
    #     for arg in self.cast_args:
    #         if arg is True:
    #             return False  # found an argument that is true
    #
    #     # Did not find a True value
    #     return True
    # else:
    #     raise Exception("Run self.cast_parameters(paramlist) first")


def fn_empty(args):
    for arg in args:
        if arg is None or arg == "":
            return True

    return False

    # if self.cast_args:
    #     # If there are any arguments, it is not empty.
    #     for arg in self.cast_args:
    #         if arg is None or arg == "":
    #             return True
    #
    #     return False
    #
    # else:
    #     raise Exception("Run self.cast_parameters(paramlist) first")

def xs_date(args):
    if len(args) == 0:
        return False
    else:
        date = parse_date(args)
        return date

def xs_yearMonthDuration(args):


    if len(args) == 0:
        return False
    else:
        duration = parse_duration(args)
        return duration

def xs_dayTimeDuration(args):
    if len(args) == 0:
        return False
    else:
        duration = parse_duration(args)
        return duration

def xs_qname(args):
    # Returns an xs:QName value formed using a supplied namespace URI and lexical QName.

    if isinstance(args, str):
        prefix, localname = str(args).split(":", 1)
        return QName(prefix=prefix, localname=localname)

    if len(args) == 1:
        prefix, localname = str(args[0]).split(":", 1)
        return QName(prefix=prefix, localname=localname)
    elif len(args) == 2:
        # If a namespace is given, add that to the QName as well
        prefix, localname = str(args[1]).split(":", 1)
        return QName(prefix=prefix, localname=localname, namespace=args[0])

def fn_number(args):
    # Returns an xs:QName value formed using a supplied namespace URI and lexical QName.

    # Otherwise try to cast the argument to float.
    return float(args)

functions = {
        "fn:count":fn_count,
        "fn:avg": fn_avg,
        "fn:max": fn_max,
        "fn:min": fn_min,
        "fn:sum": fn_sum,
        "fn:not": fn_not,
        "fn:empty": fn_empty,
        "fn:number": fn_number,
        "xs:date": xs_date,
        "xs:yearMonthDuration": xs_yearMonthDuration,
        "xs:dayTimeDuration": xs_dayTimeDuration,
        "xs:QName": xs_qname,

    }
# Add the initial set of functions to the registry
reg.add_functions(functions=functions, overwrite_functions=True)

def get_function(v):
    qname = v[0]
    args = list(v[1:])


    # If no prefix is defined, FN will be assumed for function calls
    if qname.prefix is None:
        qname.prefix = "fn"

    # Function name is an EQName. This name corresponds with a (buildin) function.
    # If no function is known, create a generic Function() object.
    # if qname in ["fn:count", "fn:avg", "fn:fn_max", "fn:fn_min", "fn:fn_sum"]:
    full_qname_str = qname.__repr__()

    function = reg.get_function(qname=qname)

    if function:
        if len(args) == 1:
            args = args[0]

        return partial(function, args)
    else:
        print("Cannot find function in registry")

def resolve_paths(fn, lxml_etree):
    """
    Attempt to resolve path queries

    :param lxml_etree:
    :return:
    """

    for i, arg in enumerate(fn.args):

        if hasattr(arg, "resolve_path"):
        # if isinstance(arg, path.PathExpression):
            if lxml_etree is None:
                # If there is no LXML ETree, we substitute by an empty list
                # As we would obviously not have been able to find these elements
                fn.args.pop(i)
            else:
                # Substitute the old argument for the LXML elements.
                resolved_args = arg.resolve_path(lxml_etree=lxml_etree)
                if isinstance(resolved_args, list):
                    # If a list is returned, we need to take out the original parameter and add
                    #  all found values to list
                    fn.args.pop(i)
                    fn.args.extend(resolved_args)

                    # If a single value has been returned, we can just replace the parameter
                else:
                    fn.args[i] = resolved_args

def cast_parameters(fn, paramlist):
    """
    Attempt to get the value of the parameter, function or just take the int value if available.

    :param paramlist:
    :return:
    """

    args = []
    for i, param in enumerate(fn.args):
        if isinstance(param, Parameter):
            param_value = param.resolve_parameter(paramlist=paramlist)

            # Only add the parameter if a value is given.
            if param_value is not None:

                if isinstance(param_value, list):
                    args.extend(param_value)
                else:
                    args.append(param_value)

        elif isinstance(param, float) or isinstance(param, int):
            args.append(param)

        elif isinstance(param, partial):
            # need to call function to get its value. This basically turns into a nested loop

            # First call cast_parameters
            args = cast_parameters(fn=param, paramlist=paramlist)

            # Get the value
            value = param()

            # Add this value to the list of arguments.
            args.append(value)

        else:
            print("Parameter not castable")
            # logging.warning(f"Parameter type not castable: {type(param)}")
    # fn.cast_args.extend(args)
    return args