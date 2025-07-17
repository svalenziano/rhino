using System;

using Rhino;
using Rhino.Commands;
using Rhino.PlugIns;

namespace RhinoCodePlatform.Rhino3D.Projects.Plugin
{
  public class ProjectPlugin : PlugIn
  {
    static readonly Guid s_projectId = new Guid("9398ef8d-6161-489e-9226-fcfe7d160edc");
    static readonly string s_projectData = "ew0KICAiaG9zdCI6IHsNCiAgICAibmFtZSI6ICJSaGlubzNEIiwNCiAgICAidmVyc2lvbiI6ICI4LjIwLjI1MTU3XHUwMDJCMTMwMDEiLA0KICAgICJvcyI6ICJ3aW5kb3dzIiwNCiAgICAiYXJjaCI6ICJ4NjQiDQogIH0sDQogICJpZCI6ICI5Mzk4ZWY4ZC02MTYxLTQ4OWUtOTIyNi1mY2ZlN2QxNjBlZGMiLA0KICAiaWRlbnRpdHkiOiB7DQogICAgIm5hbWUiOiAic3Zfc2NyaXB0cyIsDQogICAgInZlcnNpb24iOiAiMC4xLjMtYmV0YSIsDQogICAgInB1Ymxpc2hlciI6IHsNCiAgICAgICJlbWFpbCI6ICJzZW5vcnZhbGVuekBnbWFpbC5jb20iLA0KICAgICAgIm5hbWUiOiAiU3RldmVuIFZhbGVuemlhbm8iLA0KICAgICAgInVybCI6ICJodHRwOi8vc3R2bi51cy8iDQogICAgfSwNCiAgICAiZGVzY3JpcHRpb24iOiAiTWlzY2VsbGFuZW91cyBSaGlubzNEIHNjcmlwdHMgYnkgU3RldmVuIFZhbGVuemlhbm8uIiwNCiAgICAibGljZW5zZSI6ICJNSVQiDQogIH0sDQogICJzZXR0aW5ncyI6IHsNCiAgICAiYnVpbGRQYXRoIjogImZpbGU6Ly8vQzovVXNlcnMvc2Vub3IvQXBwRGF0YS9Sb2FtaW5nL01jTmVlbC9SaGlub2Nlcm9zLzguMC9zY3JpcHRzL3N2X3NjcmlwdHMvYnVpbGQvcmg4IiwNCiAgICAiYnVpbGRUYXJnZXQiOiB7DQogICAgICAiaG9zdCI6IHsNCiAgICAgICAgIm5hbWUiOiAiUmhpbm8zRCIsDQogICAgICAgICJ2ZXJzaW9uIjogIjgiDQogICAgICB9LA0KICAgICAgInRpdGxlIjogIlJoaW5vM0QgKDguKikiLA0KICAgICAgInNsdWciOiAicmg4Ig0KICAgIH0sDQogICAgInB1Ymxpc2hUYXJnZXQiOiB7DQogICAgICAidGl0bGUiOiAiTWNOZWVsIFlhayBTZXJ2ZXIiDQogICAgfQ0KICB9LA0KICAiY29kZXMiOiBbDQogICAgew0KICAgICAgImlkIjogIjRkYzllZGRlLWM0YWYtNDQ4OS1iMWNjLTg2ZDY1ZWMyY2Q5MyIsDQogICAgICAibGFuZ3VhZ2UiOiB7DQogICAgICAgICJpZCI6ICJtY25lZWwucHl0aG9ubmV0LnB5dGhvbiIsDQogICAgICAgICJ2ZXJzaW9uIjogIjMuOS4xMCINCiAgICAgIH0sDQogICAgICAidGl0bGUiOiAic3ZfaGVsbG9fd29ybGQiLA0KICAgICAgInRleHQiOiAiU1dsSmFVUlJjRTlVTVZKR1QyY3dTMFJSYjNSSlJrcHNXbTFXZVZwWE5XcGFVMEl3WW5sQ1UyRkhiSFZpTUU1MllsY3hkR0l5TkhWYVIzaHpTVWRzZWtsSFJtdGFSMVpyU1VkS05VbEhVbXhhYlVZeFlraFJUa05uTUV0TVUwSmFZak5WWjFreVJuVkpTRTUzV2xkT2NGcHVhMmRsVnpreFkybENlbGt6U25CalNGRm5ZMjFXZUdSWGJIbGFWekZzWW01U2VrbEhlSEJoTWxVMlJGRnZUa05wUVdkSlEwRnFTVWhKTmtsRWVIZFpWMDV5V1Zka2JFeFlUbmRhVjA1d1dtMXNiR05xTkdkWGVYZG5VRWhDYUZreWRHaGFNbFYwWXpOQ2JGa3liRzFoVjFaNVVHd3dUa05wUVdkSlEwRnFTVWhLYkdOWVZuQmpiVlowV2xjMU1HTjZiMmRRU0VKb1dUSjBhRm95VlhSak0wSnNXVEpzYldGWFZubFFhVUppVEVOQk9HTkhSbXBoTWtadVdsTXhlbU5IVm1waFYxcHdXbGhKSzFoUk1FdEVVVzluU1VOQloxSnRPWGxKUjFZMFdWY3hkMkpIVldka1IyaHdZM2xDYzJGWE5XeEpTR1J3WWtkM1oxbFlUbkpKU0ZKdldsTkNlV1JYTlRCaFZ6RnNTVWhTZGtsSGJIVmpNMUpvWWtkM1RrTnBRV2RKUTBJd1lVZFZaMkpIYkhwa1IxWnJTVWhDYUZreWRHaGFNbFo2U1VkS2JGcHRPWGxhVTBKNVpGYzFkV0ZYTlc1SlNGSnZXbE5DZWxrelNuQmpTRkUyUkZGdlRrTnBRV2RKUTBGcVNVaEtiR05ZVm5CamJWWjBXbGMxTUdONmIyZGpTR3d3WWpJeGMweERRbkphV0Vwb1kzY3dTMFJSYjJkSlEwRm5WMWM1TVVsSFRtaGlhVUp3WW01T01GbFhlSE5KU0U1M1dsZE9jRnB0YkdwSlNGcHNZMjVPY0dJeU5YcEpSemx0U1VkRloyTkhSbXBoTWtadVdsRXdTMGxEUVdkSlNGWjZZVmMxYmtsSVFuQmpRekZ6WVZkMGJFbElRbWhaTW5Sb1dqSlZaMk16UW14Wk1teHRZVmRXZVdONmIwNURaekJMU1VOQlowbERUV2RqYW05blkwaHNNR0l5TVhOUVZEQjNUR3BGZDB4cVNYTkpSM1JzWTIxR2VsQnFNSGxNYWxsMVRVRXdTMFJSYjNSSlJsWjZXbE5DYkdKdVdXZGFSMng1V2xkT01HRllXbXhKU0ZKMlNVZEdhMXBEUW1oaWFVSnNZbTVhY0dOdE9YVmlWMVoxWkVOQ2QxbFlVbTlKU0ZKMlNVaE9OV041TlhkWldGSnZTVWRHTVdSSE9YUlpXRkp3V1RKR2MySklhMDVEYVVGblNVTkJha2xIVm5Wa2FtOW5URE5DYUdSSFozWmtSemgyWlZjNU1XTnBPWHBoV0ZKc1RGaENhRmt5ZEdoYU1sWjZUSGN3UzBscFNXbEVVVzlxU1ZOQ2QyVllVbTlpTWpSNlJGRnZUa050YkhSalJ6bDVaRU5DZVdGSGJIVmlNMDVxWTIxc2QyUklUalZpYmxKb1pVTkNhR041UW5samR6QkxZVmN4ZDJJelNqQkpTRTVxWTIxc2QyUkhUblppYmxKc1pVaFJaMWxZVFdkak1rMU9RMjFzZEdOSE9YbGtRMEowV1ZoU2IwUlJiMDVEYld4MFkwYzVlV1JEUWxSbFdFNHdXbGN3VGtOdGJIUmpSemw1WkVOQ1ZHVllUakJhVnpCMVVUSTVjMkpIVm1wa1IyeDJZbTVOZFZJeVZuVmFXRXB3V1hjd1MyRlhNWGRpTTBvd1NVWktiMkZYTlhaRVVXOU9RMmN3UzJOSVNuQmlibEZ2U1d0b2JHSkhlSFpKU0dSMlkyMTRhMGxUUVhSSlNGbDZTVk5KY0E9PSINCiAgICB9DQogIF0NCn0=";

    static bool s_initialized = false;
    static dynamic s_projectServer = default;
    static object s_project = default;

    public static void Initialize()
    {
      if (s_initialized)
        return;

      s_projectServer = ProjectInterop.GetProjectServer();
      if (s_projectServer is null)
      {
        RhinoApp.WriteLine($"Error loading plugin. Missing Rhino3D platform");
        return;
      }

      // get project
      dynamic dctx = ProjectInterop.CreateInvokeContext();
      dctx.Inputs["projectAssembly"] = typeof(ProjectPlugin).Assembly;
      dctx.Inputs["projectId"] = s_projectId;
      dctx.Inputs["projectData"] = s_projectData;

      object project = default;
      if (s_projectServer.TryInvoke("plugins/v1/deserialize", dctx)
            && dctx.Outputs.TryGet("project", out project))
      {
        // server reports errors
        s_project = project;
      }

      s_initialized = true;
    }

    public static ProjectPlugin Instance { get; private set; }

    public static Rhino.Commands.Result RunCode(Command command, Guid id, RhinoDoc doc, RunMode mode)
    {
      if (s_project is null)
      {
        RhinoApp.WriteLine($"Error running command {id}. Project deserializiation failed.");
        return Rhino.Commands.Result.Failure;
      }

      dynamic rctx = ProjectInterop.CreateInvokeContext();
      rctx.Inputs["command"] = command;
      rctx.Inputs["project"] = s_project;
      rctx.Inputs["projectId"] = id;
      rctx.Inputs["doc"] = doc;
      rctx.Inputs["runMode"] = mode;

      if (s_projectServer.TryInvoke("plugins/v1/run", rctx))
      {
        if (rctx.Outputs.TryGet("commandResult", out Rhino.Commands.Result result))
        {
          return result;
        }

        return Rhino.Commands.Result.Success;
      }

      // server reports error
      else
        return Rhino.Commands.Result.Failure;
    }

    public ProjectPlugin() { Instance = this; }
  }
}
