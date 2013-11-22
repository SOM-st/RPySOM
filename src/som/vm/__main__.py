from som.vm.universe import main, Exit

if __name__ == '__main__':
    import sys
    try:
        main(sys.argv)
    except Exit as e:
        sys.exit(e.code)