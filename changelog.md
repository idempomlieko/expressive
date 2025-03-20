## v0.3.0 - Thursday, March 20
- Following a lot of small bug fixes and beta testing on the local branch, we are proud to announce version v0.3.0. This version brings every basic feature we wanted out of Expressive at the start. There are still quite a lot of things to flesh out and fix, and a lot more features we plan on adding.
- **Added** /expression_list, a dynamic list which allows you to look through all the expressions in your server, 10 at a time, and open each one up for more details
- **Added** /expression_info, which shows more information on a given expression.
- **Added** /expression_role to allow admins to set who can manage expressions
- **Added** /expression_logs to monitor actions regarding expressions. You can choose which events you log, too!
- **Fixed** pings not working while setting a trigger if trigger_type was user, resulting in a "User not found!" error
- **Removed** serverside logs for expressions

## v0.2.2 - Friday, March 14
- **Added** /expression_edit, which lets you edit already existing expressions
- **Added** a new icon, which is used as the profile picture + header
- **Changed** the contents of /expression_guide to better guide the user
- **Changed** all occurences of "preset" in `README.md` to "expression"


## v0.2.1 - Saturday, March 8
- **Extracted** file handling
- **Changed** all occurences of preset to expression
- **Changed** gitignore
- Courtesy of v0.2.1 goes to TomChovanec
- **Changed** /help and other commands to be visible to all chat participants (ephemeral=False)
- **Removed** the /expression command, as it had no functionality beyond being a secondary *help* command
- **Added** the /expression_delete command
- **Added** server count in custom status


## v0.2 - Saturday, March 8
- **Added commands** for help, expressive, expression_list, expression_guide
- **Changed** preset to expression - functionality remains same, name change only for thematic purposes.
- **Changed** name for **/preset_new** to **/expression_new**
- **Changed** the way IDs were assigned and data per server was handled. Now each server has it's own JSON file containing basic info and all expressions.
- **Changed** code sorting for readability.
- **Changed** README.md to reflect on new changes and fixed errors in the guide.