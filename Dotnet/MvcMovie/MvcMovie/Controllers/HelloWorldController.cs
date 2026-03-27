using Microsoft.AspNetCore.Mvc;
using System.Text.Encodings.Web;

namespace MvcMovie.Controllers;

public class HelloWorldController : Controller
{
    // GET: /HelloWorld/
    public string Index()
    {
        return "To jest moja domyślna akcja...";
    }

    // GET: /HelloWorld/Welcome/ 
    public string Welcome()
    {
        return "To jest metoda akcji Welcome...";
    }
}