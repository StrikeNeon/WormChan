# WormChan
Now you can have ALL the mems
This script will allow you to take all the resources(pics, swfs, pdfs etc.) that are on boards specified in relevants.
for some weird reason the resources are not placed in their respective directories, i'm figuring it out.
The relevants array can now be of any lenght, the structure has been modified in such a way that it will create a pair of threads if the array has more than one board and will then add to those threads via list pop method, if or when the array has less than one board(at all or left), it will create one thread, if the array is 0 it will finish the operation
