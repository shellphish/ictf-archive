/* Copyright (C) 2003 
 *    Reliable Software Group, UC Santa Barbara <rsg@cs.ucsb.edu>
 *
 * This file is part of the Capture The Flag Scorebot
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#ifndef CONFIGFILE_HPP
#define CONFIGFILE_HPP

#include <string>
#include <fstream>
#include <vector>

using namespace std;



class Tokenizer {
public:
  Tokenizer(ifstream* in);
  
  bool eat();
  string getToken();
  static string quoteString(const string& s);
  

private:
  enum State {pre, comment, quote, quote_escape, txt} state;
  ifstream* in;
  string token;
};


#endif
