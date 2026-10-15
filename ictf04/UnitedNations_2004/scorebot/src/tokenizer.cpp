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

#include "tokenizer.hpp"
#include <iostream>

using namespace std;

void parseError(Tokenizer& tok) {
  string token =  tok.getToken();
  if (token != "")
    cerr << "Unexpected token: " << tok.getToken() << endl;
  else 
    cerr << "Unexpected EOF" << endl;
}



Tokenizer::Tokenizer(ifstream* in) {
  state = pre;
  this->in = in;
  token = "";
}

bool Tokenizer::eat(){
  char current = 0;
  token = "";

  while (in->good()) {
    current = in->get();
    switch(state) {
    case pre:
      if (current == '#'){
	state = comment;
      }
      else if (current == '\"'){
	state = quote;
      }
      else if (current == ';' || current == '{' || current == '}') {
	token = current;
	return true;
      }
      else if (!isspace(current)){
	state = txt;
	token += current;
      }
      // Else whilespace, stay in pre.
      break;
    case comment:
      if(current == '\n'){
	state = pre;
      }
      // Else stay in comment
      break;
    case quote:
      if(current == '\"') {
	state = pre;
	return true;
      }
      else if (current == '\\'){
	state = quote_escape;
      }
      else {
	token += current;
      }
      break;
    case quote_escape:
      state = quote;
      token += current;
      break;
    case txt:
       if (current == '#'){
	state = comment;
	return true;
      }
      else if (current == '\"'){
	state = quote;
	return true;
      }
      else if (current == ';' || current == '{' || current == '}') {
	state = pre;
	in->putback(current);
	return true;
      }
      else if (isspace(current)){
	state = pre;
	return true;
      }
       else {
	 // Else non-space, stay in txt.
	 token += current;
       }
      break;
    }
  }
  return false;
}

string Tokenizer::getToken(){
  return token;
}

string Tokenizer::quoteString(const string& s) {
  string ret = "\"";
  string::size_type p1 = 0;
  string::size_type p2 = 0;
  
  while ((p2 = s.find_first_of("\"\\", p1)) != string::npos) {
    ret.append(s.substr(p1, p2-p1));
    if(s[p2] == '\"') {
      ret.append("\\\"");
    }
    else if (s[p2] == '\\') {
      ret.append("\\\\");
    }
    p1 = p2 + 1;
  }
  
  ret.append(s.substr(p1));
  ret.append("\"");
  return ret;
}
